
import ccxt
import pandas as pd

def fetch_ohlc(symbol="BTC", timeframe="3m", limit=100):
    exchange = ccxt.binance()
    market_symbol = symbol.upper() + "/USDT"
    try:
        ohlc = exchange.fetch_ohlcv(market_symbol, timeframe, limit=limit)
    except ccxt.BaseError as e:
        raise ValueError(f"Symbol {market_symbol} not found on Binance: {str(e)}")
    df = pd.DataFrame(ohlc, columns=["timestamp", "open", "high", "low", "close", "volume"])
    return df
