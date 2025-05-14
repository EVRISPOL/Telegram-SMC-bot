# Σκοπός: Εφαρμόζει όλους τους βασικούς τεχνικούς δείκτες
# (RSI, MACD, EMA, VWAP, OBV, ATR, Bollinger, StochRSI, ADX)
# πάνω σε ένα DataFrame με δεδομένα candlesticks.
# Χρησιμοποιείται από το trading bot για τη λήψη αποφάσεων.

import pandas as pd
# Υπολογισμός RSI (Relative Strength Index)
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df
# Υπολογισμός MACD (με histogram και bullish/bearish cross)
def calculate_macd(df):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist
    df['MACD_Cross'] = ['bullish' if m > s else 'bearish' for m, s in zip(macd, signal)]
    return df
# Υπολογισμός EMA Ribbon και προσδιορισμός τάσης (bullish/bearish)
def calculate_ema_ribbon(df):
    ema_values = [8, 13, 21, 34, 55]
    for period in ema_values:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    # trend: bullish if short EMA > long EMA
    df['EMA_Trend'] = ['bullish' if df['EMA_8'].iloc[i] > df['EMA_55'].iloc[i] else 'bearish' for i in range(len(df))]
    return df
# Υπολογισμός VWAP (Volume Weighted Average Price)
def calculate_vwap(df):
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df
# Υπολογισμός OBV (On Balance Volume) και της τάσης του
def calculate_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i - 1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])

    df['OBV'] = obv  # ✅ τώρα έχει ίδιο μήκος με το df
    df['OBV_Trend'] = df['OBV'].diff().apply(lambda x: 'up' if x > 0 else 'down' if x < 0 else 'flat')
    return df
# Υπολογισμός ATR (Average True Range) για εκτίμηση μεταβλητότητας
def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=period).mean()
    return df
# Υπολογισμός Bollinger Bands και ελέγχει για breakout
def calculate_bollinger_bands(df, period=20, std_dev=2):
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    df['BB_Upper'] = upper
    df['BB_Lower'] = lower
    df['Boll_Breakout'] = ['up' if c > u else 'down' if c < l else 'none'
                           for c, u, l in zip(df['close'], upper, lower)]
    return df
# Υπολογισμός Stochastic RSI (K και D γραμμές)
def calculate_stochastic_rsi(df, period=14, smooth_k=3, smooth_d=3):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    stoch_rsi = (rsi - rsi.rolling(window=period).min()) / (rsi.rolling(window=period).max() - rsi.rolling(window=period).min())
    df['StochRSI_K'] = stoch_rsi.rolling(window=smooth_k).mean()
    df['StochRSI_D'] = df['StochRSI_K'].rolling(window=smooth_d).mean()
    return df
# Υπολογισμός ADX (Average Directional Index)
def calculate_adx(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']

    plus_dm = high.diff()
    minus_dm = low.diff()

    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()

    df['adx'] = adx
    return df

def calculate_volume_profile(df, bins=40):
    try:
        price_volume = df[['close', 'volume']].copy()
        price_volume['price_bin'] = pd.cut(price_volume['close'], bins)
        grouped = price_volume.groupby('price_bin')['volume'].sum()
        max_bin = grouped.idxmax()
        poc_range = max_bin.mid  # Κέντρο του bin
        df['POC'] = poc_range
    except Exception as e:
        df['POC'] = df['close'].iloc[-1]  # fallback
    return df

def calculate_tsi(df, r=25, s=13):
    price_change = df['close'].diff()
    abs_price_change = price_change.abs()

    ema1 = price_change.ewm(span=r, adjust=False).mean()
    ema2 = ema1.ewm(span=s, adjust=False).mean()

    abs_ema1 = abs_price_change.ewm(span=r, adjust=False).mean()
    abs_ema2 = abs_ema1.ewm(span=s, adjust=False).mean()

    tsi = 100 * (ema2 / abs_ema2)
    df['TSI'] = tsi
    return df

# apply_indicators: Εφαρμόζει όλους τους δείκτες βήμα-βήμα
# και εκτυπώνει το μήκος του df σε κάθε στάδιο για έλεγχο.

def apply_indicators(df):
    df = calculate_rsi(df)
    print("Μετά το RSI:", len(df))

    df = calculate_macd(df)
    print("Μετά το MACD:", len(df))

    df = calculate_ema_ribbon(df)
    print("Μετά το EMA Ribbon:", len(df))

    df = calculate_vwap(df)
    print("Μετά το VWAP:", len(df))

    print("📍 ΠΡΙΝ το OBV:", len(df))
    df = calculate_obv(df)
    print("Μετά το OBV:", len(df))
    print("📍 Μήκος OBV στήλης:", len(df['OBV']))

    df = calculate_atr(df)
    print("Μετά το ATR:", len(df))

    df = calculate_bollinger_bands(df)
    print("Μετά το Bollinger Bands:", len(df))

    df = calculate_stochastic_rsi(df)
    print("Μετά το Stochastic RSI:", len(df))

    df = calculate_adx(df)
    print("Μετά το ADX:", len(df))

    df = calculate_volume_profile(df)
    print("Μετά το Volume Profile (POC):", len(df))
    
    df = calculate_tsi(df)
    print("Μετά το TSI:", len(df))


    return df
