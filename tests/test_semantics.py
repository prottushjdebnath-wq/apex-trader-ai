import pytest
from scanner.utils import check_alignment

def test_check_alignment():
    # LONG / BULLISH = aligned
    assert check_alignment("LONG", "BULLISH") is True

    # LONG / BEARISH = not aligned
    assert check_alignment("LONG", "BEARISH") is False

    # SHORT / BEARISH = aligned
    assert check_alignment("SHORT", "BEARISH") is True

    # SHORT / BULLISH = not aligned
    assert check_alignment("SHORT", "BULLISH") is False

    # either direction / NEUTRAL = not aligned
    assert check_alignment("LONG", "NEUTRAL") is False
    assert check_alignment("SHORT", "NEUTRAL") is False

    # lowercase test
    assert check_alignment("long", "bullish") is True
    assert check_alignment("short", "bearish") is True
