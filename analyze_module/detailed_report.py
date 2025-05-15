
def generate_detailed_report(ind, signal, win_percent, mtf_result=True):
    confirmations = {
        'RSI': ind['rsi'] < 30 if signal == 'LONG' else ind['rsi'] > 70,
        'MACD': ind['macd_cross'] == ('bullish' if signal == 'LONG' else 'bearish'),
        'EMA Trend': ind['ema_trend'] == ('bullish' if signal == 'LONG' else 'bearish'),
        'VWAP': ind['price'] > ind['vwap'] if signal == 'LONG' else ind['price'] < ind['vwap'],
        'ADX': ind['adx'] > 25,
        'OBV Trend': ind['obv_trend'] == ('up' if signal == 'LONG' else 'down'),
        'ATR': ind['atr'] < ind['atr_sma'],
        'Bollinger': ind['bollinger_breakout'] == ('up' if signal == 'LONG' else 'down'),
        'MTF Trend': mtf_result,
        'TSI': ind['tsi'] > 0 if signal == 'LONG' else ind['tsi'] < 0,
        'POC': ind['price'] > ind['poc'] if signal == 'LONG' else ind['price'] < ind['poc'],
        'candle': ind['candle_pattern'] in ['hammer', 'bullish_engulfing'] if signal == 'LONG' else ind['candle_pattern'] in ['inverted_hammer', 'bearish_engulfing'],
    }

    confirmations_lines = "\n".join([f"• {k}: {'✅' if v else '❌'}" for k, v in confirmations.items()])
     
    volume_boost = False
    try:
        volume_boost = ind['volume'] > ind['avg_volume'] * 1.5
    except:
        pass

    alignment_boost = False
    try:
        if signal == 'LONG' and float(ind['price']) > float(ind['vwap']) and float(ind['price']) > float(ind['poc']):
           alignment_boost = True
        elif signal == 'SHORT' and float(ind['price']) < float(ind['vwap']) and float(ind['price']) < float(ind['poc']):
           alignment_boost = True
    except Exception as e:
        print(f"⚠️ Σφάλμα στον alignment boost (detailed report): {e}")
    
    tp_proximity_boost = False
    try:
        if signal == 'LONG' and abs(ind['tp1'] - ind['swing_high']) < ind['atr']:
            tp_proximity_boost = True
        elif signal == 'SHORT' and abs(ind['tp1'] - ind['swing_low']) < ind['atr']:
            tp_proximity_boost = True 
    except:
        pass

    return f"""**[ Τεχνική Ανάλυση - Πλήρες Report ]**

📊 Κατεύθυνση Τάσης
RSI: {ind['rsi']} → {'Oversold ❗' if ind['rsi'] < 30 else 'Overbought ❗' if ind['rsi'] > 70 else ''}  
MACD: {'Bullish' if ind['macd_cross']=='bullish' else 'Bearish'} {'✔️' if (ind['macd_histogram'] > 0 if signal=='LONG' else ind['macd_histogram'] < 0) else '❌'} (Histogram: {ind['macd_histogram']})  
StochRSI: K={ind['stochrsi_k']} / D={ind['stochrsi_d']} → {'Oversold ❗' if ind['stochrsi_k'] < 20 else 'Overbought ❗' if ind['stochrsi_k'] > 80 else ''}  

📈 Τάση & Κίνηση
EMA Trend: {ind['ema_trend'].capitalize()}  
VWAP: {ind['vwap']} → Price {'Above' if ind['price'] > ind['vwap'] else 'Below'} 
ADX: {ind['adx']} → {'Very Strong Trend ‼️' if ind['adx'] > 25 else 'Weak'}  

📉 Όγκοι / Ροή
Volume: {ind['volume']} (Avg: {ind['avg_volume']:.2f}) → {'🔥 Υψηλός' if volume_boost else 'OK'}
OBV: {ind['obv']} (Trend: {ind['obv_trend']})  

🌐 Μεταβλητότητα
ATR: {ind['atr']} (Avg: {ind['atr_sma']})  
Bollinger: {ind['bollinger_breakout']} breakout

TSI: {ind['tsi']} → {'Bullish' if ind['tsi'] > 0 else 'Bearish'}  
POC: {ind['poc']} → Price {'Above' if ind['price'] > ind['poc'] else 'Below'}  

⚠️ Συμπέρασμα
→ {signal} σήμα με βάση τα περισσότερα στοιχεία.  
→ AI WIN Prediction:
• TP1: {win_percent}%
• TP2: {max(win_percent - 10, 0)}%
• TP3: {max(win_percent - 20, 0)}%
• SL: {100 - win_percent}%

📌 Ενισχυτικά Στοιχεία:
• Volume Boost: {'✅' if volume_boost else '❌'}
• POC + VWAP Alignment: {'✅' if alignment_boost else '❌'}
• TP1 κοντά σε Swing High/Low: {'✅' if tp_proximity_boost else '❌'}

✅ Επιβεβαιώσεις:
{confirmations_lines}
"""
