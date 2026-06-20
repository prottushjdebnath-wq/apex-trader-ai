import ccxt
import pandas as pd
from config.settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)
from telegram.telegram_alerts import TelegramAlerts


class ApexScanner:

    def __init__(self):

        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

        self.telegram = TelegramAlerts(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID
        )

    def get_pairs(self, limit=50):

        tickers = self.exchange.fetch_tickers()

        rows = []

        for symbol, ticker in tickers.items():

            if not symbol.endswith("/USDT:USDT"):
                continue

            rows.append({
                "symbol": symbol,
                "volume": ticker.get(
                    "quoteVolume",
                    0
                ),
                "change": ticker.get(
                    "percentage",
                    0
                )
            })

        df = pd.DataFrame(rows)

        return (
            df.sort_values(
                by="volume",
                ascending=False
            )
            .head(limit)
        )

    def get_data(self, symbol):

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe="5m",
            limit=100
        )

        df = pd.DataFrame(
            candles,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )

        return df

    def calculate_rvol(self, df):

        current_volume = df["volume"].iloc[-1]

        avg_volume = (
            df["volume"]
            .iloc[-21:-1]
            .mean()
        )

        if avg_volume == 0:
            return 0

        return round(
            current_volume / avg_volume,
            2
        )

    def trend_filter(self, df):

        df["ema20"] = (
            df["close"]
            .ewm(span=20)
            .mean()
        )

        df["ema50"] = (
            df["close"]
            .ewm(span=50)
            .mean()
        )

        return (
            df["ema20"].iloc[-1]
            >
            df["ema50"].iloc[-1]
        )

    def breakout(self, df):

        recent_high = (
            df["high"]
            .iloc[-21:-1]
            .max()
        )

        current_close = (
            df["close"]
            .iloc[-1]
        )

        return current_close > recent_high

    def trade_levels(self, df):

        entry = df["close"].iloc[-1]

        atr = (
            df["high"] - df["low"]
        ).rolling(14).mean().iloc[-1]

        sl = entry - atr
        tp1 = entry + atr
        tp2 = entry + (atr * 2)

        return (
            round(entry, 6),
            round(sl, 6),
            round(tp1, 6),
            round(tp2, 6)
        )

    def score(self,
              rvol,
              trend,
              breakout):

        score = 0

        score += min(
            rvol * 20,
            60
        )

        if trend:
            score += 20

        if breakout:
            score += 20

        return round(score, 2)

    def alert(self, row):

        message = f"""
🚀 APEX SIGNAL

Coin: {row['symbol']}
Score: {row['score']}
RVOL: {row['rvol']}

Trend: Bullish
Breakout: YES

Entry: {row['entry']}
SL: {row['sl']}
TP1: {row['tp1']}
TP2: {row['tp2']}
"""

        self.telegram.send(message)

    def run(self):

        pairs = self.get_pairs()

        results = []

        for _, row in pairs.iterrows():

            symbol = row["symbol"]

            try:

                df = self.get_data(symbol)

                rvol = self.calculate_rvol(df)

                trend = self.trend_filter(df)

                breakout = self.breakout(df)

                entry, sl, tp1, tp2 = (
                    self.trade_levels(df)
                )

                score = self.score(
                    rvol,
                    trend,
                    breakout
                )

                results.append({
                    "symbol": symbol,
                    "rvol": rvol,
                    "score": score,
                    "entry": entry,
                    "sl": sl,
                    "tp1": tp1,
                    "tp2": tp2
                })

            except Exception:
                pass

        ranked = pd.DataFrame(results)

        ranked = ranked.sort_values(
            by="score",
            ascending=False
        )

        print(
            ranked.head(10)
        )

        for _, row in ranked.head(5).iterrows():

            if row["score"] >= 70:

                self.alert(row)


if __name__ == "__main__":

    ApexScanner().run()