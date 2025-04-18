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

    sweep_detected = False
    sweep_type = None
    recent_highs = [v[2] for v in swings if v[0] == "high"]
    recent_lows = [v[2] for v in swings if v[0] == "low"]
    high_sweep = max(recent_highs) if recent_highs else None
    low_sweep = min(recent_lows) if recent_lows else None

    if high_sweep and df["high"].iloc[-1] > high_sweep:
        sweep_detected = True
        sweep_type = "buy"
    elif low_sweep and df["low"].iloc[-1] < low_sweep:
        sweep_detected = True
        sweep_type = "sell"

    if not sweep_detected:
        raise ValueError("No liquidity sweep detected – no valid entry setup.")

    choch_index = swings[-1][1] if swings else None

    ob_index = None
    if choch_index:
        for i in range(choch_index - 1, 0, -1):
            if bias == "bullish" and df["close"][i] < df["open"][i]:
                ob_index = i
                break
            elif bias == "bearish" and df["close"][i] > df["open"][i]:
                ob_index = i
                break

    if ob_index is None:
        raise ValueError("No valid Order Block found")

    ob_high = df["high"][ob_index]
    ob_low = df["low"][ob_index]
    close_now = df["close"].iloc[-1]

    fvg_detected, fvg_zone = detect_fvg(df)
    if not fvg_detected:
        raise ValueError("No Fair Value Gap detected – skipping entry.")

    if bias == "bullish":
        if close_now > ob_high:
            entry = close_now
            sl = ob_low
            tp1 = entry + (entry - sl) * 1.5
            tp2 = entry + (entry - sl) * 3
        else:
            raise ValueError("No bullish break above OB yet")
    elif bias == "bearish":
        if close_now < ob_low:
            entry = close_now
            sl = ob_high
            tp1 = entry - (sl - entry) * 1.5
            tp2 = entry - (sl - entry) * 3
        else:
            raise ValueError("No bearish break below OB yet")
    else:
        raise ValueError("No clear market bias")

    return {
        "entry": round(entry, 4),
        "sl": round(sl, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "bias": bias,
        "structure": structure[-5:],  # τελευταίες 5 δομές
        "choch_index": choch_index,
        "ob_index": ob_index,
        "liquidity_sweep": sweep_detected,
        "sweep_type": sweep_type,
        "fvg_detected": fvg_detected,
        "fvg_zone": fvg_zone
    }
