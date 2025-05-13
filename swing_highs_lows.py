
import pandas as pd

def find_swing_highs_lows(df: pd.DataFrame, lookback: int = 5) -> dict:
    """
    Εντοπίζει swing highs και swing lows σε ένα candlestick DataFrame.
    Ένα swing high είναι κερί που έχει υψηλότερο high από τα x προηγούμενα και x επόμενα.
    Ένα swing low είναι κερί που έχει χαμηλότερο low από τα x προηγούμενα και x επόμενα.

    :param df: DataFrame με στήλες ['high', 'low']
    :param lookback: Πλήθος κερίων δεξιά/αριστερά που ελέγχει
    :return: Λεξικό με swing highs και lows (index + τιμή)
    """
    swing_highs = []
    swing_lows = []

    for i in range(lookback, len(df) - lookback):
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]

        prev_highs = df['high'].iloc[i - lookback:i]
        next_highs = df['high'].iloc[i + 1:i + 1 + lookback]
        prev_lows = df['low'].iloc[i - lookback:i]
        next_lows = df['low'].iloc[i + 1:i + 1 + lookback]

        if high > max(prev_highs) and high > max(next_highs):
            swing_highs.append((i, high))

        if low < min(prev_lows) and low < min(next_lows):
            swing_lows.append((i, low))

    return {
        'highs': swing_highs,
        'lows': swing_lows
    }
