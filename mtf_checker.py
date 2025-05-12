# Ελέγχει αν η κατεύθυνση (LONG/SHORT) σε μεγαλύτερο timeframe (MTF) συμφωνεί με το προβλεπόμενο σήμα.     
# Περιγραφή:
# Η συνάρτηση λαμβάνει:
# symbol: Το κρυπτονόμισμα (π.χ. BTCUSDT)
# mtf_timeframe: Το μεγαλύτερο timeframe (π.χ. 1h, 4h)
# expected_direction: Η κατεύθυνση σήματος από μικρότερο timeframe ('long' ή 'short')

from binance_utils import get_klines
from apply_indicators import calculate_macd, calculate_ema_ribbon

def check_mtf_confirmation(symbol: str, mtf_timeframe: str, expected_direction: str) -> dict:
    try:
        df_mtf = get_klines(symbol, interval=mtf_timeframe)
        df_mtf = calculate_macd(df_mtf)
        df_mtf = calculate_ema_ribbon(df_mtf)

        last = df_mtf.iloc[-1]

        ema_trend = last['EMA_Trend']
        macd_cross = last['MACD_Cross']

        results = {
            'ema_trend_mtf': '✅' if ema_trend.lower() == expected_direction.lower() else '❌',
            'macd_trend_mtf': '✅' if macd_cross.lower() == expected_direction.lower() else '❌'
        }

        return results
    except Exception as e:
        return {
            'ema_trend_mtf': f'❌ (error: {e})',
            'macd_trend_mtf': f'❌ (error: {e})'
        }

