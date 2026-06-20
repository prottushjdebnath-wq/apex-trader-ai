from database.performance_tracker import (
    PerformanceTracker
)


class PaperTrader:

    def __init__(
        self,
        balance=1000
    ):

        self.balance = balance

        self.tracker = (
            PerformanceTracker()
        )

    def long(
        self,
        symbol,
        entry,
        exit_price,
        size
    ):

        pnl = (
            exit_price - entry
        ) * size

        self.balance += pnl

        self.tracker.add_trade(
            symbol,
            "LONG",
            entry,
            exit_price,
            pnl
        )

        return pnl

    def short(
        self,
        symbol,
        entry,
        exit_price,
        size
    ):

        pnl = (
            entry - exit_price
        ) * size

        self.balance += pnl

        self.tracker.add_trade(
            symbol,
            "SHORT",
            entry,
            exit_price,
            pnl
        )

        return pnl


if __name__ == "__main__":

    trader = PaperTrader()

    pnl = trader.long(
        "BTCUSDT",
        100000,
        101000,
        0.01
    )

    print("PNL:", pnl)
    print("Balance:", trader.balance)