
import pandas as pd

def calculate_rsi(df: pd.DataFrame, period: int = 14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi
    return df

def calculate_macd(df: pd.DataFrame):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    return df

def calculate_ema_ribbon(df: pd.DataFrame):
    emas = [8, 13, 21, 34, 55]
    for period in emas:
        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df

def calculate_vwap(df: pd.DataFrame):
    vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    df['VWAP'] = vwap
    return df

def calculate_obv(df: pd.DataFrame):
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i - 1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i - 1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    df['OBV'] = obv
    return df

def calculate_atr(df: pd.DataFrame, period: int = 14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    df['ATR'] = atr
    return df

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2):
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df['BB_Upper'] = sma + (std_dev * std)
    df['BB_Lower'] = sma - (std_dev * std)
    return df
