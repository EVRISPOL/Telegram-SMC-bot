
import pandas as pd

def is_swing_high(df, i):
    return df["high"][i] > df["high"][i-1] and df["high"][i] > df["high"][i+1]

def is_swing_low(df, i):
    return df["low"][i] < df["low"][i-1] and df["low"][i] < df["low"][i+1]

def detect_fvg(df):
    for i in range(2, len(df)):
        high_0 = df["high"].iloc[i - 2]
        low_2 = df["low"].iloc[i]
        low_0 = df["low"].iloc[i - 2]
        high_2 = df["high"].iloc[i]

        if low_2 > high_0:
            return True, (low_2, high_0)
        if high_2 < low_0:
            return True, (high_2, low_0)
    return False, None

def classify_structure(swings):
    structure = []
    for i in range(2, len(swings)):
        prev = swings[i-2]
        curr = swings[i]
        if prev[0] == "high" and curr[0] == "high":
            structure.append("HH" if curr[2] > prev[2] else "LH")
        elif prev[0] == "low" and curr[0] == "low":
            structure.append("HL" if curr[2] > prev[2] else "LL")
    return structure

def determine_bias(structure):
    if len(structure) < 2:
        return "neutral"
    if structure[-2:] == ["HH", "HL"] or structure[-2:] == ["HL", "HH"]:
        return "bullish"
    if structure[-2:] == ["LL", "LH"] or structure[-2:] == ["LH", "LL"]:
        return "bearish"
    return "neutral"

def detect_smc_signals(df):
    df = df.copy().reset_index(drop=True)
    swings = []

    for i in range(1, len(df) - 1):
        if is_swing_high(df, i):
            swings.append(("high", i, df["high"][i]))
        elif is_swing_low(df, i):
            swings.append(("low", i, df["low"][i]))

    structure = classify_structure(swings)
    bias = determine_bias(structure)

    # --- Scoring system ---
    score = 0

    # Sweep
    sweep_detected = False
    sweep_type = "none"
    recent_highs = [v[2] for v in swings if v[0] == "high"]
    recent_lows = [v[2] for v in swings if v[0] == "low"]
    high_sweep = max(recent_highs) if recent_highs else None
    low_sweep = min(recent_lows) if recent_lows else None

    if high_sweep and df["high"].iloc[-1] > high_sweep:
        sweep_detected = True
        sweep_type = "buy"
        score += 1
    elif low_sweep and df["low"].iloc[-1] < low_sweep:
        sweep_detected = True
        sweep_type = "sell"
        score += 1

    # CHoCH
    choch_index = swings[-1][1] if swings else None
    if choch_index:
        score += 2

    # Order Block
    ob_index = None
    if choch_index:
        for i in range(choch_index - 1, 0, -1):
            if bias == "bullish" and df["close"][i] < df["open"][i]:
                ob_index = i
                break
            elif bias == "bearish" and df["close"][i] > df["open"][i]:
                ob_index = i
                break
    if ob_index is not None:
        score += 2

    # FVG
    fvg_detected, fvg_zone = detect_fvg(df)
    if fvg_detected:
        score += 1

    # Decision threshold
    entry = score >= 4

    return {
        "entry": entry,
        "score": score,
        "bias": bias,
        "sweep": sweep_type,
        "choch_index": choch_index,
        "order_block_index": ob_index,
        "fvg_zone": fvg_zone if fvg_detected else None
    }
