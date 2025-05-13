from smart_sl import calculate_smart_sl

def calculate_trade_levels(df, direction, atr_multiplier=1.5, rr1=1.5, rr2=2.5, rr3=3.5):
    latest = df.iloc[-1]
    entry = latest['close']
    sl = calculate_smart_sl(df, direction, atr_multiplier)

    if direction == "LONG":
        tp1 = entry + (entry - sl) * rr1
        tp2 = entry + (entry - sl) * rr2
        tp3 = entry + (entry - sl) * rr3
    elif direction == "SHORT":
        tp1 = entry - (sl - entry) * rr1
        tp2 = entry - (sl - entry) * rr2
        tp3 = entry - (sl - entry) * rr3
    else:
        tp1 = tp2 = tp3 = None

    return round(entry, 4), round(sl, 4), round(tp1, 4), round(tp2, 4), round(tp3, 4)