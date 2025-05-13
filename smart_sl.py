# smart_sl.py

def calculate_smart_sl(df, direction, atr_multiplier=1.5):
    """
    Υπολογίζει έξυπνο Stop Loss με βάση ATR και πρόσφατα swing highs/lows.
    
    :param df: DataFrame με candlesticks και ATR
    :param direction: 'LONG' ή 'SHORT'
    :param atr_multiplier: Πολλαπλασιαστής ATR για fallback SL
    :return: Τιμή SL (float)
    """
    entry = df['close'].iloc[-1]
    atr = df['ATR'].iloc[-1]

    # Επιλογή παραθύρου pivot ανάλογα με μέγεθος TF
    swing_window = 5 if len(df) >= 10 else 3

    if direction == "LONG":
        recent_low = df['low'].rolling(window=swing_window).min().iloc[-2]
        atr_sl = entry - atr * atr_multiplier
        sl = min(atr_sl, recent_low * 0.999)  # λίγο κάτω από swing low

    elif direction == "SHORT":
        recent_high = df['high'].rolling(window=swing_window).max().iloc[-2]
        atr_sl = entry + atr * atr_multiplier
        sl = max(atr_sl, recent_high * 1.001)  # λίγο πάνω από swing high

    else:
        sl = None

    return round(sl, 4)