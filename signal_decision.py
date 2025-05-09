
def decide_signal(df):
    latest = df.iloc[-1]

    confirmations = {}

    # EMA Ribbon (trend)
    emas = [latest[f"EMA_{p}"] for p in [8, 13, 21, 34, 55]]
    if all(x < y for x, y in zip(emas, emas[1:])):  # αυξανόμενη σειρά
        confirmations["EMA_RIBBON"] = "LONG"
    elif all(x > y for x, y in zip(emas, emas[1:])):  # φθίνουσα σειρά
        confirmations["EMA_RIBBON"] = "SHORT"
    else:
        confirmations["EMA_RIBBON"] = "NONE"

    # RSI
    rsi = latest["RSI"]
    if rsi < 30:
        confirmations["RSI"] = "LONG"
    elif rsi > 70:
        confirmations["RSI"] = "SHORT"
    else:
        confirmations["RSI"] = "NONE"

    # MACD
    if latest["MACD"] > latest["MACD_Signal"]:
        confirmations["MACD"] = "LONG"
    elif latest["MACD"] < latest["MACD_Signal"]:
        confirmations["MACD"] = "SHORT"
    else:
        confirmations["MACD"] = "NONE"

    # VWAP
    if latest["close"] > latest["VWAP"]:
        confirmations["VWAP"] = "LONG"
    elif latest["close"] < latest["VWAP"]:
        confirmations["VWAP"] = "SHORT"
    else:
        confirmations["VWAP"] = "NONE"

    # OBV (προσέγγιση: ανοδική ή καθοδική τάση)
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-5]:
        confirmations["OBV"] = "LONG"
    elif df["OBV"].iloc[-1] < df["OBV"].iloc[-5]:
        confirmations["OBV"] = "SHORT"
    else:
        confirmations["OBV"] = "NONE"

    # ATR (όχι direction αλλά ένδειξη volatility - το κρατάμε ενημερωτικά)
    confirmations["ATR"] = round(latest["ATR"], 2)

    # Bollinger Bands
    if latest["close"] < latest["BB_Lower"]:
        confirmations["BOLLINGER"] = "LONG"
    elif latest["close"] > latest["BB_Upper"]:
        confirmations["BOLLINGER"] = "SHORT"
    else:
        confirmations["BOLLINGER"] = "NONE"

    # Απόφαση σήματος
    long_votes = sum(1 for v in confirmations.values() if v == "LONG")
    short_votes = sum(1 for v in confirmations.values() if v == "SHORT")

    if long_votes > short_votes:
        signal = "LONG"
    elif short_votes > long_votes:
        signal = "SHORT"
    else:
        signal = "NO CLEAR DIRECTION"

    return signal, confirmations
