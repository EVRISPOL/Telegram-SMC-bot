
from apply_indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_ema_ribbon,
    calculate_vwap,
    calculate_obv,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_stochastic_rsi
)

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
