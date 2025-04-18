def detect_smc_signals(df):
    last_close = df["close"].iloc[-1]
    last_low = df["low"].iloc[-1]
    last_high = df["high"].iloc[-1]

    direction = "long" if last_close > df["open"].iloc[-1] else "short"

    if direction == "long":
        entry = last_close
        sl = last_low
        tp1 = entry + (entry - sl) * 1.5
        tp2 = entry + (entry - sl) * 3
    else:
        entry = last_close
        sl = last_high
        tp1 = entry - (sl - entry) * 1.5
        tp2 = entry - (sl - entry) * 3

    return {"entry": round(entry, 4), "sl": round(sl, 4), "tp1": round(tp1, 4), "tp2": round(tp2, 4)}
