import ccxt
import pandas as pd


class RVOLEngine:

    def __init__(self):
        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

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

        current_volume = df["volume"].iloc[-1]
        average_volume = df["volume"].iloc[:-1].mean()

        if average_volume == 0:
            return 0

        return round(
            current_volume / average_volume,
            2
        )