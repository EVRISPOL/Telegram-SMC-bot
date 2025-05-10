
def evaluate_indicators(indicators: dict) -> str:
    """
    Αξιολογεί τους τεχνικούς δείκτες και επιστρέφει 'LONG', 'SHORT' ή 'NEUTRAL'.
    
    :param indicators: Λεξικό με τα δεδομένα των δεικτών
    :return: Κατεύθυνση σήματος
    """

    score_long = 0
    score_short = 0

    # === RSI ===
    if indicators['rsi'] < 30:
        score_long += 2
    elif indicators['rsi'] > 70:
        score_short += 2
    elif 40 <= indicators['rsi'] <= 50:
        score_long += 1
        score_short += 1

    # === MACD ===
    if indicators['macd_cross'] == 'bullish':
        score_long += 2
    elif indicators['macd_cross'] == 'bearish':
        score_short += 2

    if indicators['macd_histogram'] > 0:
        score_long += 1
    elif indicators['macd_histogram'] < 0:
        score_short += 1

    # === OBV ===
    if indicators['obv_trend'] == 'up':
        score_long += 2
    elif indicators['obv_trend'] == 'down':
        score_short += 2

    # === VWAP ===
    if indicators['price'] > indicators['vwap']:
        score_long += 1
    elif indicators['price'] < indicators['vwap']:
        score_short += 1

    # === EMA Ribbon ===
    if indicators['ema_trend'] == 'bullish':
        score_long += 2
    elif indicators['ema_trend'] == 'bearish':
        score_short += 2

    # === ATR ===
    if indicators['atr'] < indicators['atr_sma']:
        score_long += 1
        score_short += 1
    elif indicators['atr'] > 2 * indicators['atr_sma']:
        score_long -= 1
        score_short -= 1

    # === Bollinger Bands ===
    if indicators['bollinger_breakout'] == 'up':
        score_long += 2
    elif indicators['bollinger_breakout'] == 'down':
        score_short += 2

    # === Stochastic RSI ===
    if indicators['stochrsi_k'] < 20 and indicators['stochrsi_d'] < 20:
        score_long += 1
    elif indicators['stochrsi_k'] > 80 and indicators['stochrsi_d'] > 80:
        score_short += 1

    # === ADX ===
    if indicators['adx'] < 20:
        score_long -= 1
        score_short -= 1
    elif indicators['adx'] > 25:
        score_long += 1
        score_short += 1

    # === Απόφαση ===
    if score_long > score_short:
        return 'LONG'
    elif score_short > score_long:
        return 'SHORT'
    else:
        return 'NEUTRAL'
