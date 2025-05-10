import sys   # Διαχείριση των path της Python (sys.path) για import modules από άλλους φακέλους
import os    # Λήψη του τρέχοντος directory και δημιουργία πλήρους (absolute) path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Προσθέτουμε το root directory στο path για να δουλεύουν τα imports από φακέλους όπως trade_levels.py
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from binance_utils import get_klines
from mtf_checker import check_mtf_confirmation
from evaluate_indicators import evaluate_indicators
from apply_indicators import apply_indicators
from trade_levels import calculate_trade_levels
from chart_generator import generate_chart

# Βήματα
SYMBOL, TIMEFRAME, LEVERAGE, RISK, CAPITAL, MTF = range(6)

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def analyze_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🪙 Πληκτρολόγησε το symbol (π.χ. BTCUSDT):")
    return SYMBOL

async def receive_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["symbol"] = update.message.text.strip().upper()
    await update.message.reply_text("⏱️ Πληκτρολόγησε το timeframe (π.χ. 15m, 1h):")
    return TIMEFRAME

async def receive_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["timeframe"] = update.message.text.strip()
    await update.message.reply_text("📈 Πληκτρολόγησε το leverage (π.χ. 10):")
    return LEVERAGE

async def receive_leverage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["leverage"] = update.message.text.strip()
    await update.message.reply_text("⚠️ Πληκτρολόγησε το risk % (π.χ. 2):")
    return RISK

async def receive_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["risk"] = update.message.text.strip()
    await update.message.reply_text("💰 Πληκτρολόγησε το capital (π.χ. 300):")
    return CAPITAL

async def receive_capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["capital"] = update.message.text.strip()
    await update.message.reply_text("📊 Πληκτρολόγησε το MTF timeframe (ή γράψε skip):")
    return MTF

async def receive_mtf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text.strip()
    valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']

    if value.lower() not in valid_timeframes and value.lower() != "skip":
        await update.message.reply_text("❌ Λάθος MTF timeframe. Επιτρεπτά: 15m, 1h, 4h, 1d... Ή πληκτρολόγησε 'skip'.")
        return MTF

    context.user_data["mtf"] = value.lower()
    await update.message.reply_text("✅ Καταχωρήθηκε το MTF timeframe.")
    return await finalize_analysis(update, context)

async def finalize_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            'adx': last['ADX'],
        }

        signal = evaluate_indicators(indicators)
        entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df, signal)

        mtf_result = None
        if user_data.get("mtf") and user_data["mtf"].lower() != "skip":
            mtf_result = check_mtf_confirmation(symbol, user_data["mtf"], signal)

        conf_lines = [
            f"📢 Signal: {signal}",
            f"🎯 Entry: {entry}",
            f"🛑 SL: {sl}",
            f"🎯 TP1: {tp1}",
            f"🎯 TP2: {tp2}",
            f"🎯 TP3: {tp3}",
            f"\n📊 Confirmations:"
        ]

        for key, val in indicators.items():
            conf_lines.append(f"- {key}: {val}")

        if mtf_result:
            conf_lines.append("\n🧭 MTF Confirmation:")
            for key, val in mtf_result.items():
                conf_lines.append(f"- {key}: {val}")

        response = "\n".join(conf_lines)
        chart = generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3)

        await update.message.reply_photo(photo=chart, caption=response, reply_markup=ReplyKeyboardRemove())
        summary = f"📈 Ολοκληρώθηκε η ανάλυση για {symbol}."
        await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"❌ Σφάλμα κατά την ανάλυση: {str(e)}", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Η ανάλυση ακυρώθηκε.", reply_markup=ReplyKeyboardRemove())
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
