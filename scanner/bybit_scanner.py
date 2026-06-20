import ccxt
import pandas as pd


class BybitScanner:

    def __init__(self):
        self.exchange = ccxt.bybit({
            "enableRateLimit": True,
        })

    def get_usdt_pairs(self):
        markets = self.exchange.load_markets()

        pairs = []

        for symbol in markets:
            if (
                symbol.endswith("/USDT:USDT")
                and markets[symbol]["active"]
            ):
                pairs.append(symbol)

        return pairs

    def get_top_volume_pairs(self, limit=20):
        tickers = self.exchange.fetch_tickers()

        data = []

        for symbol, ticker in tickers.items():

            if not symbol.endswith("/USDT:USDT"):
                continue

            volume = ticker.get("quoteVolume", 0)

            data.append({
                "symbol": symbol,
                "volume": volume
            })

        df = pd.DataFrame(data)

        df = df.sort_values(
            by="volume",
            ascending=False
        )

        return df.head(limit)

    def run(self):
        top_pairs = self.get_top_volume_pairs()

        print("\nTOP VOLUME PAIRS\n")
        print(top_pairs)


if __name__ == "__main__":
    scanner = BybitScanner()
    scanner.run()