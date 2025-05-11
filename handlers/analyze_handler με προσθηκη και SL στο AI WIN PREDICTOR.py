
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

ADMIN_USER_ID = 123456789  # Βάλε εδώ το πραγματικό Telegram user ID σου

# Ζυγισμένα βάρη για κάθε δείκτη σύμφωνα με τη στρατηγική
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

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    indicator_results = {
        'rsi': True,
        'macd': True,
        'ema_trend': True,
        'adx': True,
        'vwap': False,
        'obv': True,
        'stochrsi': False,
        'bollinger': False
    }

    total_possible = sum(INDICATOR_WEIGHTS.values())
    win_score = sum(INDICATOR_WEIGHTS[key] for key, val in indicator_results.items() if val)
    win_percent = round((win_score / total_possible) * 100, 1)
    win_tp2 = round(win_percent - 10, 1)
    win_tp3 = round(win_percent - 20, 1)
    sl_percent = round(100 - win_percent, 1)

    confirmation_total = len(INDICATOR_WEIGHTS)
    confirmation_agree = sum(1 for val in indicator_results.values() if val)

    direction = "SHORT"
    entry = 103542.67
    sl = 103863.07
    tp1 = 103062.06
    tp2 = 102741.66
    tp3 = 102421.26

    message = (
        f"Signal: {direction}\n"
        f"Entry: {entry}\n"
        f"SL: {sl}\n"
        f"TP1: {tp1}\n"
        f"TP2: {tp2}\n"
        f"TP3: {tp3}\n\n"
        f"✅ Confirmations: {confirmation_agree} / {confirmation_total}\n"
        f"🎯 AI WIN Prediction:\n"
        f"• TP1: {win_percent}%\n"
        f"• TP2: {win_tp2}%\n"
        f"• TP3: {win_tp3}%\n"
        f"• SL: {sl_percent}%"
    )

    keyboard = [[InlineKeyboardButton("ℹ️ Στοιχεία", callback_data="show_details")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data["full_analysis"] = f"""
**[ Τεχνική Ανάλυση - Πλήρες Report ]**

📊 Κατεύθυνση Τάσης
RSI: 29.23 → Oversold ❗
MACD: Bearish Cross ❌ (Histogram: -64.13)
StochRSI: K=0.07 / D=0.07 → Oversold ❗

📈 Τάση & Κίνηση
EMA Trend: Bearish ❌
VWAP: 103879.93 → Price Below ❌
ADX: 52.50 → Very Strong Trend ‼️

📉 Όγκοι / Ροή
OBV: -605.10 (Trend: Up)
Volume Bars: Low Volume ⬇️

🌐 Μεταβλητότητα
ATR: 213.60 (Avg: 236.41)
Bollinger: No breakout

⚠️ Συμπέρασμα
→ Bearish σήμα με ισχυρή τάση και oversold κατάσταση.
→ AI WIN Prediction:
• TP1: {win_percent}%
• TP2: {win_tp2}%
• TP3: {win_tp3}%
• SL: {sl_percent}%
"""

    await update.message.reply_text(message, reply_markup=reply_markup)

async def show_details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id == ADMIN_USER_ID:
        full_analysis = context.user_data.get("full_analysis", "No data available.")
        await query.message.reply_text(full_analysis, parse_mode="Markdown")
    else:
        await query.message.reply_text("Δεν έχεις πρόσβαση.")
