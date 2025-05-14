
def detect_candlestick_patterns(df):
    """
    Ανιχνεύει βασικά candlestick patterns στο τελευταίο κερί.
    Προσθέτει στήλη 'candle_pattern' με την αναγνώριση.
    """
    import numpy as np

    def classify_candle(open_, high, low, close):
        body = abs(close - open_)
        range_ = high - low
        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low

        if body < range_ * 0.1:
            return 'doji'
        elif close > open_ and lower_wick > 2 * body and upper_wick < body:
            return 'hammer'
        elif open_ > close and upper_wick > 2 * body and lower_wick < body:
            return 'inverted_hammer'
        elif i >= 1 and close > df.iloc[i-1]['open'] and open_ < df.iloc[i-1]['close']:
            return 'bullish_engulfing'
        elif i >= 1 and open_ > df.iloc[i-1]['close'] and close < df.iloc[i-1]['open']:
            return 'bearish_engulfing'
        else:
            return 'none'

    patterns = []
    for i in range(len(df)):
        o, h, l, c = df.iloc[i][['open', 'high', 'low', 'close']]
        patterns.append(classify_candle(o, h, l, c))

    df['candle_pattern'] = patterns
    return df
