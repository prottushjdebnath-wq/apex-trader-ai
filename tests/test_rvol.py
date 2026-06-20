from scanner.rvol_engine import RVOLEngine
from scanner.bybit_scanner import BybitScanner

rvol = RVOLEngine()
scanner = BybitScanner()

pairs = scanner.get_top_volume_pairs(20)

for symbol in pairs["symbol"].tolist():

    try:
        score = rvol.calculate_rvol(symbol)

        print(
            f"{symbol:<20} RVOL={score}"
        )

    except Exception:
        pass