# Εισαγωγή συναρτήσεων που εφαρμόζουν τεχνικούς δείκτες στο DataFrame
from strategy.apply_indicators import (
    calculate_rsi,                     # Δείκτης RSI (Relative Strength Index)
    calculate_macd,                    # Δείκτης MACD (Moving Average Convergence Divergence)
    calculate_ema_ribbon,              # EMA Ribbon - σύστημα εκθετικών κινητών μέσων
    calculate_vwap,                    # VWAP - Volume Weighted Average Price
    calculate_obv,                     # OBV - On Balance Volume
    calculate_atr,                     # ATR - Average True Range (μεταβλητότητα)
    calculate_bollinger_bands,         # Bollinger Bands (εύρος τιμής)
    calculate_stochastic_rsi,          # Stochastic RSI (οσκιλλοσκόπηση RSI)
    calculate_adx                      # ADX - Average Directional Index (ισχύς τάσης)
)
# Εφαρμόζει όλους τους τεχνικούς δείκτες στο DataFrame των τιμών
def apply_indicators(df):
    df = calculate_rsi(df)                   # Υπολογισμός MACD και MACD Histogram
    df = calculate_macd(df)                  # Προσθήκη EMA τάσης
    df = calculate_ema_ribbon(df)            # Υπολογισμός VWAP
    df = calculate_vwap(df)                  # Υπολογισμός OBV και τάσης OBV
    df = calculate_obv(df)                   # Υπολογισμός ATR (μεταβλητότητας)
    df = calculate_atr(df)                   # Προσθήκη Bollinger breakout
    df = calculate_bollinger_bands(df)       # Υπολογισμός Stochastic RSI (K και D)
    df = calculate_stochastic_rsi(df)        # Υπολογισμός Stochastic RSI (K και D)
    df = calculate_adx(df)                   # Υπολογισμός ADX (ισχύς τάσης)
    return df                                # Επιστρέφει το DataFrame με όλους τους δείκτες
