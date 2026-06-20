import ccxt


class OIEngine:

    def __init__(self):

        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

    def get_open_interest(self, symbol):

        try:

            oi = self.exchange.fetch_open_interest(
                symbol
            )

            return float(
                oi["openInterestValue"]
            )

        except Exception as e:

            print(
                f"OI Error: {symbol}: {e}"
            )

            return 0

    def oi_change(
        self,
        current_oi,
        previous_oi
    ):

        if previous_oi == 0:
            return 0

        return round(
            (
                (
                    current_oi
                    - previous_oi
                )
                / previous_oi
            ) * 100,
            2
        )
        