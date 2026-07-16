def check_alignment(direction, regime):
    if regime == "NEUTRAL":
        return False

    direction_upper = direction.upper() if direction else ""
    regime_upper = regime.upper() if regime else ""

    if direction_upper == "LONG" and regime_upper == "BULLISH":
        return True
    if direction_upper == "SHORT" and regime_upper == "BEARISH":
        return True

    return False
