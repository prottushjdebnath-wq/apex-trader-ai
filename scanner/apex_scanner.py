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

    def get_top_pairs(self, limit=50):

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

    def calculate_rvol(
        self,
        symbol,
        timeframe="5m",
        limit=50
    ):

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit
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

        current_volume = (
            df["volume"].iloc[-1]
        )

        average_volume = (
            df["volume"]
            .iloc[:-1]
            .mean()
        )

        if average_volume == 0:
            return 0

        return round(
            current_volume
            / average_volume,
            2
        )

    def trend_filter(
        self,
        symbol,
        timeframe="5m"
    ):

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=60
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

    def calculate_score(
        self,
        rvol,
        change,
        trend
    ):

        rvol_score = min(
            rvol * 20,
            100
        )

        momentum_score = min(
            abs(change) * 5,
            100
        )

        trend_score = (
            100 if trend else 0
        )

        score = (
            rvol_score * 0.5
            + momentum_score * 0.3
            + trend_score * 0.2
        )

        return round(
            score,
            2
        )

    def send_alerts(
        self,
        ranked
    ):

        for _, row in ranked.head(5).iterrows():

            if row["score"] < 70:
                continue

            message = (
                f"🚀 APEX SIGNAL\n\n"
                f"Coin: {row['symbol']}\n"
                f"Score: {row['score']}\n"
                f"RVOL: {row['rvol']}\n"
                f"Change: {round(row['change'],2)}%\n"
                f"Trend: {'Bullish' if row['trend'] else 'Bearish'}"
            )

            self.telegram.send(
                message
            )

    def run(self):

        pairs = self.get_top_pairs()

        results = []

        for _, row in pairs.iterrows():

            symbol = row["symbol"]

            try:

                rvol = (
                    self.calculate_rvol(
                        symbol
                    )
                )

                trend = (
                    self.trend_filter(
                        symbol
                    )
                )

                score = (
                    self.calculate_score(
                        rvol,
                        row["change"],
                        trend
                    )
                )

                results.append({
                    "symbol": symbol,
                    "rvol": rvol,
                    "change": row["change"],
                    "trend": trend,
                    "score": score
                })

            except Exception:
                continue

        ranked = pd.DataFrame(
            results
        )

        ranked = ranked.sort_values(
            by="score",
            ascending=False
        )

        print(
            "\nAPEX TOP OPPORTUNITIES\n"
        )

        print(
            ranked.head(10)
        )

        self.send_alerts(
            ranked
        )


if __name__ == "__main__":

    ApexScanner().run()