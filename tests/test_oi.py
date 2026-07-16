import pytest
from scanner.oi_engine import OIEngine

def test_oi_confirmation():
    engine = OIEngine()

    # Unavailable data
    # current_oi > 0, previous_oi = 0
    engine.get_historical_open_interest = lambda x: (100.0, 0.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is True
    assert res["oi_confirmed"] is False
    assert res["oi_change_pct"] == 0.0

    # No data at all
    engine.get_historical_open_interest = lambda x: (0.0, 0.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is False
    assert res["oi_confirmed"] is False
    assert res["oi_change_pct"] == 0.0

    # Flat
    engine.get_historical_open_interest = lambda x: (100.0, 100.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is True
    assert res["oi_confirmed"] is False
    assert res["oi_change_pct"] == 0.0

    # Declining
    engine.get_historical_open_interest = lambda x: (90.0, 100.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is True
    assert res["oi_confirmed"] is False
    assert res["oi_change_pct"] == -10.0

    # +2.9%
    engine.get_historical_open_interest = lambda x: (102.9, 100.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is True
    assert res["oi_confirmed"] is False
    assert res["oi_change_pct"] == 2.9

    # +3.0%
    engine.get_historical_open_interest = lambda x: (103.0, 100.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is True
    assert res["oi_confirmed"] is True
    assert res["oi_change_pct"] == 3.0

    # +5.0%
    engine.get_historical_open_interest = lambda x: (105.0, 100.0)
    res = engine.check_oi_confirmation("BTCUSDT")
    assert res["oi_data_available"] is True
    assert res["oi_confirmed"] is True
    assert res["oi_change_pct"] == 5.0
