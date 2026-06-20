class RiskEngine:

    def __init__(
        self,
        account_balance,
        risk_percent=2
    ):
        self.account_balance = account_balance
        self.risk_percent = risk_percent

    def position_size(
        self,
        entry_price,
        stop_price
    ):

        risk_amount = (
            self.account_balance
            * self.risk_percent
            / 100
        )

        stop_distance = abs(
            entry_price - stop_price
        )

        if stop_distance == 0:
            return 0

        size = (
            risk_amount
            / stop_distance
        )

        return round(size, 4)