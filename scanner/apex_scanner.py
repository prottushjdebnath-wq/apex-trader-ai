import ccxt
import pandas as pd


class ApexScanner:

    def __init__(self):

        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

    def get_top_pairs(self, limit=30):

        tickers = self.exchange.fetch_tickers()

        data = []

        for symbol, ticker in tickers.items():

            if not symbol.endswith("/USDT:USDT"):
                continue

            volume = ticker.get(
                "quoteVolume",
                0
            )

            change = ticker.get(
                "percentage",
                0
            )

            data.append({
                "symbol": symbol,
                "volume": volume,
                "change": change
            })

        df = pd.DataFrame(data)

        df = df.sort_values(
            by="volume",
            ascending=False
        )

        return df.head(limit)

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

        avg_volume = (
            df["volume"]
            .iloc[:-1]
            .mean()
        )

        if avg_volume == 0:
            return 0

        return round(
            current_volume / avg_volume,
            2
        )

    def ema_filter(
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

    def score(
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

        final_score = (
            rvol_score * 0.5
            +
            momentum_score * 0.3
            +
            trend_score * 0.2
        )

        return round(
            final_score,
            2
        )

    def run(self):

        pairs = self.get_top_pairs()

        results = []

        for _, row in pairs.iterrows():

            symbol = row["symbol"]

            try:

                rvol = self.calculate_rvol(
                    symbol
                )

                trend = self.ema_filter(
                    symbol
                )

                score = self.score(
                    rvol,
                    row["change"],
                    trend
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

        ranked = pd.DataFrame(results)

        ranked = ranked.sort_values(
            by="score",
            ascending=False
        )

        print("\nAPEX TOP OPPORTUNITIES\n")

        print(
            ranked.head(10)
        )


if __name__ == "__main__":

    ApexScanner().run()