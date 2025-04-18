
import ccxt
import pandas as pd

def fetch_ohlc(symbol="BTC", timeframe="3m", limit=100):
    exchange = ccxt.binance()
    exchange.load_markets()
    
    market_symbol = symbol.upper() + "/USDT"
    if market_symbol not in exchange.symbols:
        raise ValueError(f"❌ Symbol {market_symbol} not found on Binance.")
    
    try:
        ohlc = exchange.fetch_ohlcv(market_symbol, timeframe, limit=limit)
    except ccxt.BaseError as e:
        raise ValueError(f"⚠️ Failed to fetch data for {market_symbol}: {str(e)}")
    
    df = pd.DataFrame(ohlc, columns=["timestamp", "open", "high", "low", "close", "volume"])
    return df
