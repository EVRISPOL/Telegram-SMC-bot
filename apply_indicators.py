
import pandas as pd

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal

    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist
    df['MACD_Cross'] = (macd > signal).map({True: 'bullish', False: 'bearish'})
    return df


def calculate_ema_ribbon(df):
    ema_values = [8, 13, 21, 34, 55]
    for period in ema_values:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    # trend: bullish if short EMA > long EMA
    df['EMA_Trend'] = ['bullish' if df['EMA_8'].iloc[i] > df['EMA_55'].iloc[i] else 'bearish' for i in range(len(df))]
    return df

def calculate_vwap(df):
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df

def calculate_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    df['OBV_Trend'] = ['up' if df['OBV'].iloc[i] > df['OBV'].iloc[i-1] else 'down' for i in range(1, len(df))]
    df['OBV_Trend'] = ['none'] + df['OBV_Trend']  # align with length
    return df

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=period).mean()
    return df

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

def calculate_stochastic_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    df['StochRSI_K'] = stoch_rsi * 100
    df['StochRSI_D'] = df['StochRSI_K'].rolling(3).mean()
    return df

def calculate_adx(df, period=14):
    df['TR'] = df[['high', 'low', 'close']].max(axis=1) - df[['high', 'low', 'close']].min(axis=1)

    df['+DM'] = df['high'].diff()
    df['-DM'] = df['low'].diff()
    df['+DM'] = df['+DM'].where((df['+DM'] > df['-DM']) & (df['+DM'] > 0), 0.0)
    df['-DM'] = df['-DM'].where((df['-DM'] > df['+DM']) & (df['-DM'] > 0), 0.0)

    atr = df['TR'].rolling(window=period).mean()
    plus_di = 100 * (df['+DM'].rolling(window=period).mean() / atr)
    minus_di = 100 * (df['-DM'].rolling(window=period).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    df['ADX'] = dx.rolling(window=period).mean()
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
    df = calculate_adx(df)
    return df
