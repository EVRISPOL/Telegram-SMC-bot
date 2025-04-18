import ta

def check_indicators(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["macd"] = ta.trend.MACD(df["close"]).macd_diff()

    last_rsi = df["rsi"].iloc[-1]
    last_macd = df["macd"].iloc[-1]

    confirmed = last_rsi > 50 and last_macd > 0
    return {"rsi": last_rsi, "macd": last_macd, "confirmed": confirmed}
