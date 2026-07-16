import pytest
import pandas as pd
from scanner.apex_scanner import ApexScanner

def test_risk_reward_ratio():
    scanner = ApexScanner()

    # Create dummy DataFrame
    # For LONG: entry=100, recent_low=90, atr=2, recent_high=120
    # sl = 90 - 2 = 88
    # tp1 = 120 (since 120 > 100)
    # risk = 100 - 88 = 12
    # reward = 120 - 100 = 20
    # rr = 20 / 12 = 1.67
    df_long = pd.DataFrame({
        "high": [120]*20 + [102],
        "low": [90]*20 + [98],
        "close": [110]*20 + [100]
    })

    # Mock rolling ATR to return 2
    df_long["high"] = df_long["high"].astype(float)
    df_long["low"] = df_long["low"].astype(float)
    df_long.loc[20, "high"] = 102
    df_long.loc[20, "low"] = 98 # so high - low = 4, but we'll mock rolling

    # We will just patch pd.core.window.rolling.Rolling.mean to return 2 for this test
    original_mean = pd.core.window.rolling.Rolling.mean
    pd.core.window.rolling.Rolling.mean = lambda self: pd.Series([2.0]*21)

    try:
        _, sl, tp1, _, rr = scanner.trade_levels(df_long, "LONG")
        assert sl == 88.0
        assert tp1 == 120.0
        assert rr == pytest.approx(1.67, 0.01)

        # For SHORT: entry=100, recent_high=110, recent_low=80, atr=2
        # sl = 110 + 2 = 112
        # tp1 = 80 (since 80 < 100)
        # risk = 112 - 100 = 12
        # reward = 100 - 80 = 20
        # rr = 20 / 12 = 1.67
        df_short = pd.DataFrame({
            "high": [110]*20 + [102],
            "low": [80]*20 + [98],
            "close": [90]*20 + [100]
        })
        _, sl, tp1, _, rr = scanner.trade_levels(df_short, "SHORT")
        assert sl == 112.0
        assert tp1 == 80.0
        assert rr == pytest.approx(1.67, 0.01)

        # Fallback LONG: tp candidate < entry
        df_long_fallback = pd.DataFrame({
            "high": [95]*20 + [102],
            "low": [90]*20 + [98],
            "close": [92]*20 + [100]
        })
        _, sl, tp1, _, rr = scanner.trade_levels(df_long_fallback, "LONG")
        # sl = 90 - 2 = 88. risk = 12
        # tp1 fallback = 100 + 4 = 104. reward = 4
        # rr = 4 / 12 = 0.33
        assert tp1 == 104.0
        assert rr == pytest.approx(0.33, 0.01)

    finally:
        pd.core.window.rolling.Rolling.mean = original_mean
