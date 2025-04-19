
import ta
import pandas as pd

def check_indicators(df):
    result = {
        "rsi": None,
        "macd": None,
        "volume": None,
        "confirmed": True,
        "reasons": []
    }

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    rsi = df["rsi"].iloc[-1]
    result["rsi"] = rsi
    if rsi > 70:
        result["confirmed"] = False
        result["reasons"].append("RSI overbought (>70)")
    elif rsi < 30:
        result["confirmed"] = False
        result["reasons"].append("RSI oversold (<30)")

    # MACD
    macd = ta.trend.MACD(df["close"])
    df["macd_line"] = macd.macd()
    df["signal_line"] = macd.macd_signal()  # Corrected: Using macd_signal for the signal line

    # Detect MACD crossovers
    macd_cross = df["macd_line"].iloc[-2] < df["signal_line"].iloc[-2] and df["macd_line"].iloc[-1] > df["signal_line"].iloc[-1]
    macd_bear_cross = df["macd_line"].iloc[-2] > df["signal_line"].iloc[-2] and df["macd_line"].iloc[-1] < df["signal_line"].iloc[-1]

    # Allow long only if bullish cross
    # Allow short only if bearish cross
    if macd_cross:
        result["macd"] = "bullish"
    elif macd_bear_cross:
        result["macd"] = "bearish"
    else:
        result["confirmed"] = False
        result["reasons"].append("No MACD cross confirmation")

    # Volume
    df["vol_ma"] = df["volume"].rolling(window=20).mean()
    last_vol = df["volume"].iloc[-1]
    vol_ma = df["vol_ma"].iloc[-1]
    result["volume"] = last_vol

    if last_vol < vol_ma * 0.7:  # Low volume
        result["confirmed"] = False
        result["reasons"].append("Low volume")

    return result
