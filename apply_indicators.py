# Prepare corrected version of apply_indicators.py with safe assignment to avoid index mismatch
import pandas as pd

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = pd.Series(rsi.values, index=df.index)
    return df

def calculate_macd(df):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal

    df['MACD'] = pd.Series(macd.values, index=df.index)
    df['MACD_Signal'] = pd.Series(signal.values, index=df.index)
    df['MACD_Hist'] = pd.Series(hist.values, index=df.index)
    df['MACD_Cross'] = (df['MACD'] > df['MACD_Signal']).map({True: 'bullish', False: 'bearish'})
    return df

def calculate_ema_ribbon(df):
    ema_values = [8, 13, 21, 34, 55]
    for period in ema_values:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    df['EMA_Trend'] = [
        'bullish' if df['EMA_8'].iloc[i] > df['EMA_55'].iloc[i] else 'bearish'
        for i in range(len(df))
    ]
    return df

def calculate_vwap(df):
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df

def calculate_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i - 1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = pd.Series(obv, index=df.index)
    df['OBV_Trend'] = ['none'] + [
        'up' if obv[i] > obv[i - 1] else 'down'
        for i in range(1, len(obv))
    ]
    return df

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    df['ATR'] = pd.Series(atr.values, index=df.index)
    return df

def calculate_bollinger_bands(df, period=20, std_dev=2):
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    df['BB_Upper'] = pd.Series(upper.values, index=df.index)
    df['BB_Lower'] = pd.Series(lower.values, index=df.index)
    df['Boll_Breakout'] = [
        'up' if c > u else 'down' if c < l else 'none'
        for c, u, l in zip(df['close'], upper, lower)
    ]
    return df

def calculate_stochastic_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    df['StochRSI_K'] = pd.Series(stoch_rsi.values, index=df.index)
    df['StochRSI_D'] = pd.Series(stoch_rsi.rolling(3).mean().values, index=df.index)
    return df

def apply_indicators(df):
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_ema_ribbon(df)
    df = calculate_vwap(df)
    df = calculate_obv(df)
    df = calculate_atr(df)
    df = calculate_bollinger_bands(df)
    df = calculate_stochastic_rsi(df)
    return df


# Write the corrected code back to the file
output_path = "/mnt/data/Telegram-SMC-bot-main/Telegram-SMC-bot-main/apply_indicators.py"
with open(output_path, "w", encoding="utf-8") as file:
    file.write(corrected_apply_indicators_code)

output_path

