import ccxt
import pandas as pd
from config.settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)
from telegram.telegram_alerts import TelegramAlerts
from scanner.utils import check_alignment
from scanner.oi_engine import OIEngine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')



class ApexScanner:

    def __init__(self):

        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

        self.telegram = TelegramAlerts(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID
        )
        self.oi_engine = OIEngine()

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

    def trade_levels(self, df, direction):
        entry = df["close"].iloc[-1]

        atr = (
            df["high"] - df["low"]
        ).rolling(14).mean().iloc[-1]

        recent_high = df["high"].iloc[-21:-1].max()
        recent_low = df["low"].iloc[-21:-1].min()

        if direction.upper() == "LONG":
            sl = recent_low - atr
            tp1_candidate = recent_high

            # ATR fallback if next resistance structure is too close
            if tp1_candidate <= entry:
                tp1 = entry + (2 * atr)
            else:
                tp1 = tp1_candidate
        else: # SHORT
            sl = recent_high + atr
            tp1_candidate = recent_low

            # ATR fallback if next support structure is too close
            if tp1_candidate >= entry:
                tp1 = entry - (2 * atr)
            else:
                tp1 = tp1_candidate

        tp2 = entry + (2 * (tp1 - entry)) if direction.upper() == "LONG" else entry - (2 * (entry - tp1))

        risk = abs(entry - sl)
        reward = abs(tp1 - entry)

        risk_reward_ratio = reward / risk if risk > 0 else 0

        return (
            round(entry, 6),
            round(sl, 6),
            round(tp1, 6),
            round(tp2, 6),
            round(risk_reward_ratio, 2)
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

# Temporary diagnostic logging block
                direction = "LONG" if breakout else "SHORT"
                mtf_trend = "BULLISH" if trend else "BEARISH" # Simulated based on existing simple trend boolean
                btc_regime = "BULLISH" # Placeholder

                mtf_aligned = check_alignment(direction, mtf_trend)
                btc_aligned = check_alignment(direction, btc_regime)

                oi_info = self.oi_engine.check_oi_confirmation(symbol)
                funding_rate = 0.01 # Placeholder
                squeeze_potential = 0.5 # Placeholder

                entry, sl, tp1, tp2, rr = (
                    self.trade_levels(df, direction)
                )

                logging.info(
                    f"FUTURES SETUP DIAGNOSTIC - "
                    f"symbol: {symbol}, direction: {direction}, mtf_trend: {mtf_trend}, "
                    f"btc_regime: {btc_regime}, mtf_aligned: {mtf_aligned}, btc_aligned: {btc_aligned}, "
                    f"oi_current: {oi_info['oi_current']}, oi_previous: {oi_info['oi_previous']}, "
                    f"oi_change_pct: {oi_info['oi_change_pct']}, oi_confirmed: {oi_info['oi_confirmed']}, "
                    f"funding_rate: {funding_rate}, squeeze_potential: {squeeze_potential}, rr: {rr}"
                )

                if rr < 1.5:
                    continue # Reject setups below 1.5R

                score = self.score(
                    rvol,
                    trend,
                    breakout
                )

                if mtf_aligned: score += 10
                if btc_aligned: score += 10
                if oi_info['oi_confirmed']: score += 10

                results.append({
                    "symbol": symbol,
                    "rvol": rvol,
                    "score": score,
                    "entry": entry,
                    "sl": sl,
                    "tp1": tp1,
                    "tp2": tp2,
                    "rr": rr
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