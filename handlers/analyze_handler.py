# Εισαγωγή απαραίτητων modules από Telegram και custom αρχεία
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from binance_utils import get_klines # Λήψη ιστορικών τιμών
from mtf_checker import check_mtf_confirmation # Έλεγχος τάσης μεγαλύτερου timeframe (MTF)
from evaluate_indicators import evaluate_indicators # Απόφαση LONG ή SHORT με βάση δείκτες
from apply_indicators import apply_indicators # Υπολογισμός τεχνικών δεικτών
from trade_levels import calculate_trade_levels  # Υπολογισμός Entry, SL, TP
from chart_generator import generate_chart  # Δημιουργία γραφήματος με τα επίπεδα

# Ορισμός των καταστάσεων του ConversationHandler
SYMBOL, TIMEFRAME, LEVERAGE, RISK, CAPITAL, MTF = range(6)
# ID admin χρήστη για εμφάνιση πλήρους report
ADMIN_USER_ID = 7316121101  # Αντικατάστησέ το με το δικό σου ID
# Βάρη ανά δείκτη για υπολογισμό WIN %
# Συνάρτηση που υπολογίζει το ποσοστό επιτυχίας βάσει επιβεβαιώσεων
def calculate_win_percent(indicators, signal):
    adx = indicators['adx']

    if adx < 20:  # Range αγορά
        weights = {
            'rsi': 2.5, 'macd': 1.0, 'ema_trend': 1.0, 'adx': 0.5,
            'vwap': 1.0, 'obv': 2.0, 'stochrsi': 1.5, 'bollinger': 2.0,
            'tsi': 1.0, 'poc': 1.5
        }
    elif adx > 25:  # Ισχυρή τάση
        weights = {
            'rsi': 1.0, 'macd': 2.5, 'ema_trend': 2.0, 'adx': 2.0,
            'vwap': 2.0, 'obv': 1.0, 'stochrsi': 0.5, 'bollinger': 0.5,
            'tsi': 2.0, 'poc': 1.5
        }
    else:  # Ενδιάμεση τάση
        weights = {
            'rsi': 2.0, 'macd': 2.0, 'ema_trend': 2.0, 'adx': 1.5,
            'vwap': 1.5, 'obv': 1.0, 'stochrsi': 1.0, 'bollinger': 1.0,
            'tsi': 1.5, 'poc': 1.5
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
    }

    total_possible = sum(weights.values())
    win_score = sum(weights[k] for k, v in results.items() if v)

    # 🔸 Alignment Boost (με safe float σύγκριση)
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

    # 🔸 Volume Boost
    try:
        if indicators['volume'] > indicators['avg_volume'] * 1.5:
            print("✅ Volume boost ενεργοποιήθηκε!")
            win_score += 1
        else:
            print("ℹ️ Volume boost δεν εφαρμόστηκε.")
    except Exception as e:
        print(f"⚠️ Σφάλμα στον υπολογισμό volume boost: {e}")

    # 🔸 TP Proximity Boost
    try:
        if signal == 'LONG':
            if abs(indicators['tp1'] - indicators['swing_high']) < indicators['atr']:
                print("✅ TP1 κοντά σε swing high (LONG) → boost")
                win_score += 1
        elif signal == 'SHORT':
            if abs(indicators['tp1'] - indicators['swing_low']) < indicators['atr']:
                print("✅ TP1 κοντά σε swing low (SHORT) → boost")
                win_score += 1
        else:
            print("ℹ️ Δεν πληρούνται οι προϋποθέσεις proximity.")
    except Exception as e:
        print(f"⚠️ Σφάλμα στο TP proximity check: {e}")

    win_percent = round((win_score / (total_possible + 3)) * 100, 1)
    return win_percent, results

# Αρχή της συνομιλίας - ζητά symbol
async def analyze_start(update, context):
    await update.message.reply_text("🪙 Πληκτρολόγησε το symbol (π.χ. BTCUSDT):")
    return SYMBOL
# Λήψη symbol από τον χρήστη
async def receive_symbol(update, context):
    context.user_data["symbol"] = update.message.text.strip().upper()
    await update.message.reply_text("⏱️ Πληκτρολόγησε το timeframe (π.χ. 15m, 1h):")
    return TIMEFRAME
# Λήψη timeframe
async def receive_timeframe(update, context):
    user_input = update.message.text.strip().lower()
    valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']

    if user_input not in valid_timeframes:
        await update.message.reply_text("❗ Μη έγκυρο timeframe. Πληκτρολόγησε ένα από τα: 1m, 3m, 5m, 15m, 1h, 4h, 1d...")
        return TIMEFRAME  # Επαναλαμβάνει το ίδιο βήμα

    context.user_data["timeframe"] = user_input
    await update.message.reply_text("📈 Πληκτρολόγησε το leverage (π.χ. 10):")
    return LEVERAGE
# Λήψη leverage
async def receive_leverage(update, context):
    user_input = update.message.text.strip()
    # Έλεγχος αν είναι θετικός αριθμός
    try:
        leverage = float(user_input)
        if leverage <= 0:
            raise ValueError
        # Αποθήκευση στο context
        context.user_data["leverage"] = leverage
        await update.message.reply_text("⚠️ Πληκτρολόγησε το risk % (π.χ. 2):")
        return RISK

    except ValueError:
        await update.message.reply_text("❗ Μη έγκυρο leverage. Πληκτρολόγησε έναν θετικό αριθμό π.χ. 10:")
        return LEVERAGE  # Επαναλαμβάνει το ίδιο βήμα

# Λήψη ποσοστού ρίσκου
async def receive_risk(update, context):
    user_input = update.message.text.strip()
    # Έλεγχος αν είναι αριθμός μεταξύ 0 και 100
    try:
        risk = float(user_input)
        if risk <= 0 or risk > 100:
            raise ValueError

        context.user_data["risk"] = risk
        await update.message.reply_text("💰 Πληκτρολόγησε το capital (π.χ. 300):")
        return CAPITAL

    except ValueError:
        await update.message.reply_text("❗ Μη έγκυρο ποσοστό ρίσκου. Πληκτρολόγησε έναν αριθμό από 1 έως 100 (π.χ. 2):")
        return RISK  # Επαναλαμβάνει το ίδιο βήμα

# Λήψη κεφαλαίου
async def receive_capital(update, context):
    user_input = update.message.text.strip()
    # Έλεγχος αν είναι θετικός αριθμός
    try:
        capital = float(user_input)
        if capital <= 0:
            raise ValueError

        context.user_data["capital"] = capital
        await update.message.reply_text("📊 Πληκτρολόγησε το MTF timeframe (ή γράψε skip):")
        return MTF

    except ValueError:
        await update.message.reply_text("❗ Μη έγκυρο κεφάλαιο. Πληκτρολόγησε έναν θετικό αριθμό π.χ. 300:")
        return CAPITAL  # Επαναλαμβάνει το ίδιο βήμα

# Λήψη MTF timeframe ή skip
async def receive_mtf(update, context):
    value = update.message.text.strip()
    valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']

    if value.lower() not in valid_timeframes and value.lower() != "skip":
        await update.message.reply_text("❌ Λάθος MTF timeframe. Επιτρεπτά: 15m, 1h, 4h, 1d... Ή πληκτρολόγησε 'skip'.")
        return MTF

    context.user_data["mtf"] = value.lower()
    await update.message.reply_text("✅ Καταχωρήθηκε το MTF timeframe.")
    return await finalize_analysis(update, context)

async def finalize_analysis(update, context):
    try:
        user_data = context.user_data
        symbol = user_data["symbol"]
        timeframe = user_data["timeframe"]
        # Φόρτωση ιστορικών τιμών και εφαρμογή δεικτών
        df = get_klines(symbol, interval=timeframe)
        df = apply_indicators(df)
        last = df.iloc[-1]        
       
        # Λήψη τιμών δεικτών από τελευταία γραμμή
        indicators = {
            'rsi': last['RSI'],
            'macd_cross': last['MACD_Cross'],
            'macd_histogram': last['MACD_Hist'],
            'obv_trend': last['OBV_Trend'],
            'obv': last['OBV'],
            'price': last['close'],
            'vwap': last['VWAP'],
            'ema_trend': last['EMA_Trend'],
            'atr': last['ATR'],
            'atr_sma': df['ATR'].rolling(14).mean().iloc[-1],
            'bollinger_breakout': last['Boll_Breakout'],
            'stochrsi_k': last['StochRSI_K'],
            'stochrsi_d': last['StochRSI_D'],
            'adx': last['adx'],
            'tsi': last['TSI'],  # ✅ Νέος δείκτης TSI
            'poc': last['POC'],  # ✅ Νέος δείκτης POC
            'candle_pattern': last['candle_pattern'],# ✅νεο 
        }
        # Εκτίμηση LONG ή SHORT σήματος 
        signal = evaluate_indicators(indicators)
        # Υπολογισμός Entry, SL, TP
        entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df, signal)
        # Εμπλουτισμος των indicators με tp1, atr, swing_high, swing_low volume
        indicators.update({
            'volume': last['volume'], # Εξασφαλισμένο volume
            'avg_volume': df['volume'].rolling(20).mean().iloc[-1], #✅ ΝΕΟ
            'tp1': tp1, #✅ ΝΕΟ
            'atr': last['ATR'], #✅ ΝΕΟ
            'swing_high': last['swing_high'], #✅ ΝΕΟ
            'swing_low': last['swing_low'], #✅ ΝΕΟ
        })
         # Υπολογισμός πιθανότητας επιτυχίας και αριθμός επιβεβαιώσεων
        win_percent, confirmations = calculate_win_percent(indicators, signal)
        confirmation_count = sum(1 for v in confirmations.values() if v)
        total_confirmations = len(confirmations)
         # Έλεγχος τάσης μεγαλύτερου timeframe αν δόθηκε
        mtf_result = None
        if user_data.get("mtf") and user_data["mtf"].lower() != "skip":
            mtf_result = check_mtf_confirmation(symbol, user_data["mtf"], signal)
        # Υπολογισμός μεγέθους θέσης
        capital = float(user_data["capital"])
        risk = float(user_data["risk"])
        leverage = float(user_data["leverage"])
        position_size = capital * leverage
        risk_amount = round(capital * (risk / 100), 2)

        # Συνάρτηση υπολογισμού κέρδους για κάθε TP
        def calculate_profit(entry, target, size):
            return round((size * (target - entry) / entry), 2)

        # Υπολογισμός κερδών ανά TP
        profit_tp1 = calculate_profit(entry, tp1, position_size)
        profit_tp2 = calculate_profit(entry, tp2, position_size)
        profit_tp3 = calculate_profit(entry, tp3, position_size)
        
        # Δημιουργία απάντησης με τα επίπεδα και προβλέψεις
        response = (
            f"📢 Signal: {signal}\\n"
            f"🎯 Entry: {entry}\\n\n"
            f"🛑 SL: {sl}\\n\n"
            f"🎯 TP1: {tp1}  (+{profit_tp1}€)\n"
            f"🎯 TP2: {tp2}  (+{profit_tp2}€)\n"
            f"🎯 TP3: {tp3}  (+{profit_tp3}€)\n\n"
            f"💸 Μέγιστη ζημία (SL): -{risk_amount}€\n"
            f"✅ Confirmations: {confirmation_count} / {total_confirmations}\\n"
            f"📊 MTF Trend: {'✅ Συμφωνία' if mtf_result else '❌ Διαφωνία'}\n\n"
            f"🎯 AI WIN Prediction:\n\n"
            f"• TP1: {round(win_percent, 1)}%\\n"
            f"• TP2: {round(max(win_percent - 10, 0), 1)}%\\n"
            f"• TP3: {round(max(win_percent - 20, 0), 1)}%\\n"
            f"• SL: {round(100 - win_percent, 1)}%"
        )
         # Inline κουμπί για προβολή στοιχείων
        keyboard = [[InlineKeyboardButton("ℹ️ Στοιχεία", callback_data="show_details")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
         # Δημιουργία chart και αποστολή μηνύματος με caption + image
        chart = generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3)
        context.user_data['full_analysis'] = generate_detailed_report(indicators, signal, win_percent, mtf_result if mtf_result is not None else True)

        await update.message.reply_photo(photo=chart, caption=response, reply_markup=reply_markup)
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"❌ Σφάλμα κατά την ανάλυση: {str(e)}", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
# Callback για εμφάνιση πλήρους ανάλυσης (μόνο admin)
async def show_details_callback(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id == ADMIN_USER_ID:
        full_report = context.user_data.get("full_analysis", "Δεν υπάρχουν δεδομένα.")
        await query.message.reply_text(full_report, parse_mode="Markdown")
    else:
        await query.message.reply_text("Δεν έχεις πρόσβαση.")
# Δημιουργία πλήρους αναφοράς (για admin view)
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

    confirmations_lines = "\\n".join([f"• {k}: {'✅' if v else '❌'}" for k, v in confirmations.items()])
     
    # Νέα Επιβεβαίωση: Volume Boost
    volume_boost = False
    try:
        volume_boost = ind['volume'] > ind['avg_volume'] * 1.5
    except:
        pass
    # Νέα Επιβεβαίωση: POC + VWAP alignment
    # Νέα Επιβεβαίωση: POC + VWAP alignment
    alignment_boost = False
    try:
        if signal == 'LONG' and float(ind['price']) > float(ind['vwap']) and float(ind['price']) > float(ind['poc']):
           alignment_boost = True
        elif signal == 'SHORT' and float(ind['price']) < float(ind['vwap']) and float(ind['price']) < float(ind['poc']):
           alignment_boost = True
    except Exception as e:
        print(f"⚠️ Σφάλμα στον alignment boost (detailed report): {e}")
    
     # TP Proximity Boost
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
Bollinger: {ind['bollinger_breakout']} breakout\n
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
# Τερματισμός conversation σε οποιοδήποτε σημείο
def cancel(update, context):
    return ConversationHandler.END
# Επιστρέφει τον handler για την εντολή /analyze
def get_analyze_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("analyze", analyze_start)],
        states={
            SYMBOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_symbol)],
            TIMEFRAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_timeframe)],
            LEVERAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_leverage)],
            RISK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_risk)],
            CAPITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_capital)],
            MTF: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_mtf)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

