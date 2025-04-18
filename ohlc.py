import ccxt
import pandas as pd

def fetch_ohlc(symbol="BTC/USDT", timeframe="3m", limit=100):
    exchange = ccxt.binance()
    ohlc = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlc, columns=["timestamp", "open", "high", "low", "close", "volume"])
    return df
