# Δημιουργία του πλήρους αρχείου με την προσθήκη της συνάρτησης get_analyze_handler
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from binance_utils import get_klines
from mtf_checker import check_mtf_confirmation
from evaluate_indicators import evaluate_indicators
from apply_indicators import apply_indicators
from trade_levels import calculate_trade_levels
from chart_generator import generate_chart

# Conversation states
SYMBOL, TIMEFRAME, LEVERAGE, RISK, CAPITAL, MTF = range(6)

ADMIN_USER_ID = 123456789  # Αντικατάστησέ το με το δικό σου ID

INDICATOR_WEIGHTS = {
    'rsi': 2.0,
    'macd': 2.5,
    'ema_trend': 2.0,
    'adx': 1.5,
    'vwap': 1.5,
    'obv': 1.0,
    'stochrsi': 0.5,
    'bollinger': 0.5
}

def calculate_win_percent(indicators, signal):
    results = {
        'rsi': indicators['rsi'] < 30 if signal == 'LONG' else indicators['rsi'] > 70,
        'macd': indicators['macd_cross'] == ('bullish' if signal == 'LONG' else 'bearish'),
        'ema_trend': indicators['ema_trend'] == ('bullish' if signal == 'LONG' else 'bearish'),
        'adx': indicators['adx'] > 25,
        'vwap': indicators['price'] > indicators['vwap'] if signal == 'LONG' else indicators['price'] < indicators['vwap'],
        'obv': indicators['obv_trend'] == ('up' if signal == 'LONG' else 'down'),
        'stochrsi': indicators['stochrsi_k'] < 20 and indicators['stochrsi_d'] < 20 if signal == 'LONG' else indicators['stochrsi_k'] > 80 and indicators['stochrsi_d'] > 80,
        'bollinger': indicators['bollinger_breakout'] == ('up' if signal == 'LONG' else 'down')
    }

    total_possible = sum(INDICATOR_WEIGHTS.values())
    win_score = sum(INDICATOR_WEIGHTS[k] for k, v in results.items() if v)
    win_percent = round((win_score / total_possible) * 100, 1)
    return win_percent, results

async def analyze_start(update, context):
    await update.message.reply_text("🪙 Πληκτρολόγησε το symbol (π.χ. BTCUSDT):")
    return SYMBOL

async def receive_symbol(update, context):
    context.user_data["symbol"] = update.message.text.strip().upper()
    await update.message.reply_text("⏱️ Πληκτρολόγησε το timeframe (π.χ. 15m, 1h):")
    return TIMEFRAME

async def receive_timeframe(update, context):
    context.user_data["timeframe"] = update.message.text.strip()
    await update.message.reply_text("📈 Πληκτρολόγησε το leverage (π.χ. 10):")
    return LEVERAGE

async def receive_leverage(update, context):
    context.user_data["leverage"] = update.message.text.strip()
    await update.message.reply_text("⚠️ Πληκτρολόγησε το risk % (π.χ. 2):")
    return RISK

async def receive_risk(update, context):
    context.user_data["risk"] = update.message.text.strip()
    await update.message.reply_text("💰 Πληκτρολόγησε το capital (π.χ. 300):")
    return CAPITAL

async def receive_capital(update, context):
    context.user_data["capital"] = update.message.text.strip()
    await update.message.reply_text("📊 Πληκτρολόγησε το MTF timeframe (ή γράψε skip):")
    return MTF

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

        df = get_klines(symbol, interval=timeframe)
        df = apply_indicators(df)
        last = df.iloc[-1]

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
        }

        signal = evaluate_indicators(indicators)
        entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df, signal)

        win_percent, confirmations = calculate_win_percent(indicators, signal)
        confirmation_count = sum(1 for v in confirmations.values() if v)
        total_confirmations = len(confirmations)

        mtf_result = None
        if user_data.get("mtf") and user_data["mtf"].lower() != "skip":
            mtf_result = check_mtf_confirmation(symbol, user_data["mtf"], signal)

        response = (
            f"📢 Signal: {signal}\\n"
            f"🎯 Entry: {entry}\\n"
            f"🛑 SL: {sl}\\n"
            f"🎯 TP1: {tp1}\\n"
            f"🎯 TP2: {tp2}\\n"
            f"🎯 TP3: {tp3}\\n\\n"
            f"✅ Confirmations: {confirmation_count} / {total_confirmations}\\n"
            f"🎯 AI WIN Prediction:\\n"
            f"• TP1: {win_percent}%\\n"
            f"• TP2: {max(win_percent - 10, 0)}%\\n"
            f"• TP3: {max(win_percent - 20, 0)}%\\n"
            f"• SL: {100 - win_percent}%"
        )

        keyboard = [[InlineKeyboardButton("ℹ️ Στοιχεία", callback_data="show_details")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        chart = generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3)
        context.user_data['full_analysis'] = generate_detailed_report(indicators, signal, win_percent)

        await update.message.reply_photo(photo=chart, caption=response, reply_markup=reply_markup)
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"❌ Σφάλμα κατά την ανάλυση: {str(e)}", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def show_details_callback(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id == ADMIN_USER_ID:
        full_report = context.user_data.get("full_analysis", "Δεν υπάρχουν δεδομένα.")
        await query.message.reply_text(full_report, parse_mode="Markdown")
    else:
        await query.message.reply_text("Δεν έχεις πρόσβαση.")

def generate_detailed_report(ind, signal, win_percent):
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
OBV: {ind['obv']} (Trend: {ind['obv_trend']})  

🌐 Μεταβλητότητα
ATR: {ind['atr']} (Avg: {ind['atr_sma']})  
Bollinger: {ind['bollinger_breakout']} breakout  

⚠️ Συμπέρασμα
→ {signal} σήμα με βάση τα περισσότερα στοιχεία.  
→ AI WIN Prediction:
• TP1: {win_percent}%
• TP2: {max(win_percent - 10, 0)}%
• TP3: {max(win_percent - 20, 0)}%
• SL: {100 - win_percent}%
\"\"\"

def cancel(update, context):
    return ConversationHandler.END

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

