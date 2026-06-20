import ccxt
import pandas as pd


class OIRVOLScanner:

    def __init__(self):

        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

    def get_top_volume_pairs(self, limit=30):

        tickers = self.exchange.fetch_tickers()

        data = []

        for symbol, ticker in tickers.items():

            if not symbol.endswith("/USDT:USDT"):
                continue

            quote_volume = ticker.get(
                "quoteVolume",
                0
            )

            pct_change = ticker.get(
                "percentage",
                0
            )

            data.append({
                "symbol": symbol,
                "volume": quote_volume,
                "change": pct_change
            })

        df = pd.DataFrame(data)

        df = df.sort_values(
            by="volume",
            ascending=False
        )

        return df.head(limit)

    def scan(self):

        df = self.get_top_volume_pairs()

        print("\nTOP MOMENTUM COINS\n")

        print(df)

        return df


if __name__ == "__main__":

    scanner = OIRVOLScanner()

    scanner.scan()