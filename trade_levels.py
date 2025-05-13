from smart_sl import calculate_smart_sl
from swing_highs_lows import find_swing_highs_lows

def calculate_trade_levels(df, direction, atr_multiplier=1.5, rr1=1.5, rr2=2.5, rr3=3.5, mode="hybrid"):
    latest = df.iloc[-1]
    entry = latest['close']
    sl = calculate_smart_sl(df, direction, atr_multiplier)
    
    tps = []

    if mode == "rr":
        # Κλασικό RR-based TP
        if direction == "LONG":
            tps = [
                entry + (entry - sl) * rr1,
                entry + (entry - sl) * rr2,
                entry + (entry - sl) * rr3
            ]
        elif direction == "SHORT":
            tps = [
                entry - (sl - entry) * rr1,
                entry - (sl - entry) * rr2,
                entry - (sl - entry) * rr3
            ]

    elif mode == "hybrid":
        swings = find_swing_highs_lows(df)
        highs = [price for i, price in swings['highs'] if i > df.index[-10]]
        lows = [price for i, price in swings['lows'] if i > df.index[-10]]

        if direction == "LONG":
            rr_targets = [
                entry + (entry - sl) * rr1,
                entry + (entry - sl) * rr2,
                entry + (entry - sl) * rr3
            ]
            logical_highs = sorted([h for h in highs if h > entry])
            tps = [
                logical_highs[0] if len(logical_highs) > 0 and logical_highs[0] < rr_targets[0] else rr_targets[0],
                logical_highs[1] if len(logical_highs) > 1 and logical_highs[1] < rr_targets[1] else rr_targets[1],
                logical_highs[2] if len(logical_highs) > 2 and logical_highs[2] < rr_targets[2] else rr_targets[2]
            ]

        elif direction == "SHORT":
            rr_targets = [
                entry - (sl - entry) * rr1,
                entry - (sl - entry) * rr2,
                entry - (sl - entry) * rr3
            ]
            logical_lows = sorted([l for l in lows if l < entry], reverse=True)
            tps = [
                logical_lows[0] if len(logical_lows) > 0 and logical_lows[0] > rr_targets[0] else rr_targets[0],
                logical_lows[1] if len(logical_lows) > 1 and logical_lows[1] > rr_targets[1] else rr_targets[1],
                logical_lows[2] if len(logical_lows) > 2 and logical_lows[2] > rr_targets[2] else rr_targets[2]
            ]

    else:
        tps = [None, None, None]

    return round(entry, 4), round(sl, 4), round(tps[0], 4), round(tps[1], 4), round(tps[2], 4)
