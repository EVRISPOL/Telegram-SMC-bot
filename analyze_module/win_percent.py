def calculate_win_percent(indicators, signal, mtf_result=True):                 # Βάρη ανά δείκτη για υπολογισμό WIN %   # Συνάρτηση που υπολογίζει το ποσοστό επιτυχίας βάσει επιβεβαιώσεων
    adx = indicators['adx']

    if adx < 20:
        weights = {
            'rsi': 2.5, 'macd': 1.0, 'ema_trend': 1.0, 'adx': 0.5,
            'vwap': 1.0, 'obv': 2.0, 'stochrsi': 1.5, 'bollinger': 2.0,
            'tsi': 1.0, 'poc': 1.5, 'atr': 0.5, 'mtf': 1.5, 'candle': 1.0
        }
    elif adx > 25:
        weights = {
            'rsi': 1.0, 'macd': 2.5, 'ema_trend': 2.0, 'adx': 2.0,
            'vwap': 2.0, 'obv': 1.0, 'stochrsi': 0.5, 'bollinger': 0.5,
            'tsi': 2.0, 'poc': 1.5, 'atr': 1.0, 'mtf': 2.0, 'candle': 1.0
        }
    else:
        weights = {
            'rsi': 2.0, 'macd': 2.0, 'ema_trend': 2.0, 'adx': 1.5,
            'vwap': 1.5, 'obv': 1.0, 'stochrsi': 1.0, 'bollinger': 1.0,
            'tsi': 1.5, 'poc': 1.5, 'atr': 1.0, 'mtf': 1.5, 'candle': 1.0
        }

    results = {
        'rsi': indicators['rsi'] < 30 if signal == 'LONG' else indicators['rsi'] > 70,
        'macd': indicators['macd_cross'] == ('bullish' if signal == 'LONG' else 'bearish'),
        'ema_trend': indicators['ema_trend'] == ('bullish' if signal == 'LONG' else 'bearish'),
        'adx': indicators['adx'] > 25,
        'vwap': indicators['price'] > indicators['vwap'] if signal == 'LONG' else indicators['price'] < indicators['vwap'],
        'obv': indicators['obv_trend'] == ('up' if signal == 'LONG' else 'down'),
        'stochrsi': indicators['stochrsi_k'] < 20 and indicators['stochrsi_d'] < 20 if signal == 'LONG' else indicators['stochrsi_k'] > 80 and indicators['stochrsi_d'] > 80,
        'bollinger': indicators['bollinger_breakout'] == ('up' if signal == 'LONG' else 'down'),
        'tsi': indicators['tsi'] > 0 if signal == 'LONG' else indicators['tsi'] < 0,
        'poc': indicators['price'] > indicators['poc'] if signal == 'LONG' else indicators['price'] < indicators['poc'],
        'atr': indicators['atr'] > indicators['atr_sma'],
        'mtf': mtf_result,
        'candle': indicators['candle_pattern'] in ['hammer', 'bullish_engulfing'] if signal == 'LONG' else indicators['candle_pattern'] in ['inverted_hammer', 'bearish_engulfing']
    }

    total_possible = sum(weights.values())
    win_score = sum(weights[k] for k, v in results.items() if v)

    try:
        price = float(indicators['price'])
        vwap = float(indicators['vwap'])
        poc = float(indicators['poc'])
        if signal == 'LONG' and price > vwap and price > poc:
            print("✅ Alignment boost ενεργοποιήθηκε για LONG!")
            win_score += 1
        elif signal == 'SHORT' and price < vwap and price < poc:
            print("✅ Alignment boost ενεργοποιήθηκε για SHORT!")
            win_score += 1
        else:
            print("ℹ️ Δεν υπήρξε alignment boost.")
    except Exception as e:
        print(f"⚠️ Σφάλμα στον alignment boost: {e}")

    try:
        if indicators['volume'] > indicators['avg_volume'] * 1.5:
            print("✅ Volume boost ενεργοποιήθηκε!")
            win_score += 1
        else:
            print("ℹ️ Volume boost δεν εφαρμόστηκε.")
    except Exception as e:
        print(f"⚠️ Σφάλμα στον υπολογισμό volume boost: {e}")

    try:
        if signal == 'LONG' and abs(indicators['tp1'] - indicators['swing_high']) < indicators['atr']:
            print("✅ TP1 κοντά σε swing high (LONG) → boost")
            win_score += 1
        elif signal == 'SHORT' and abs(indicators['tp1'] - indicators['swing_low']) < indicators['atr']:
            print("✅ TP1 κοντά σε swing low (SHORT) → boost")
            win_score += 1
        else:
            print("ℹ️ Δεν πληρούνται οι προϋποθέσεις proximity.")
    except Exception as e:
        print(f"⚠️ Σφάλμα στο TP proximity check: {e}")

    win_percent = round((win_score / (total_possible + 3)) * 100, 1)
    return win_percent, results
