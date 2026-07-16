import ccxt
from config.settings import FUTURES_OI_CONFIRM_THRESHOLD_PCT

class OIEngine:

    def __init__(self):
        self.exchange = ccxt.bybit({
            "enableRateLimit": True
        })

    def get_open_interest(self, symbol):
        try:
            oi = self.exchange.fetch_open_interest(symbol)
            return float(oi["openInterestValue"])
        except Exception as e:
            print(f"OI Error: {symbol}: {e}")
            return 0

    def get_historical_open_interest(self, symbol, timeframe="5m", limit=2):
        # We try to use fetchOpenInterestHistory if available
        try:
            if self.exchange.has['fetchOpenInterestHistory']:
                history = self.exchange.fetch_open_interest_history(symbol, timeframe=timeframe, limit=limit)
                if len(history) >= 2:
                    current_oi = float(history[-1]['openInterestValue'])
                    previous_oi = float(history[0]['openInterestValue'])
                    return current_oi, previous_oi
                elif len(history) == 1:
                    return float(history[-1]['openInterestValue']), 0.0
            return self.get_open_interest(symbol), 0.0
        except Exception as e:
            print(f"OI History Error: {symbol}: {e}")
            return self.get_open_interest(symbol), 0.0

    def oi_change(self, current_oi, previous_oi):
        if previous_oi == 0:
            return 0
        return round(((current_oi - previous_oi) / previous_oi) * 100, 2)

    def check_oi_confirmation(self, symbol):
        current_oi, previous_oi = self.get_historical_open_interest(symbol)

        oi_data_available = (current_oi > 0) and (previous_oi > 0)

        if not oi_data_available:
            return {
                "oi_data_available": (current_oi > 0),
                "oi_current": current_oi,
                "oi_previous": previous_oi,
                "oi_change_pct": 0.0,
                "oi_confirmed": False
            }

        change_pct = self.oi_change(current_oi, previous_oi)
        confirmed = change_pct >= FUTURES_OI_CONFIRM_THRESHOLD_PCT

        return {
            "oi_data_available": True,
            "oi_current": current_oi,
            "oi_previous": previous_oi,
            "oi_change_pct": change_pct,
            "oi_confirmed": confirmed
        }
