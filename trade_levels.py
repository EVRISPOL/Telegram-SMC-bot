
def calculate_trade_levels(df, direction, atr_multiplier=1.5, rr1=1.5, rr2=2.5, rr3=3.5):
    latest = df.iloc[-1]
    entry = latest['close']
    atr = latest['ATR']

    if direction == "LONG":
        sl = entry - atr * atr_multiplier
        tp1 = entry + atr * atr_multiplier * rr1
        tp2 = entry + atr * atr_multiplier * rr2
        tp3 = entry + atr * atr_multiplier * rr3
    elif direction == "SHORT":
        sl = entry + atr * atr_multiplier
        tp1 = entry - atr * atr_multiplier * rr1
        tp2 = entry - atr * atr_multiplier * rr2
        tp3 = entry - atr * atr_multiplier * rr3
    else:
        sl = tp1 = tp2 = tp3 = None

    return round(entry, 4), round(sl, 4), round(tp1, 4), round(tp2, 4), round(tp3, 4)
