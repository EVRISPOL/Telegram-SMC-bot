# Εισαγωγή απαραίτητων modules από Telegram και custom αρχεία
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from binance_utils import get_klines # Λήψη ιστορικών τιμών
from symbol_checker import is_valid_symbol  # ελεγχος εγκυρης πληκτρολογησης signal απο symbol checker!
from strategy.mtf_checker import check_mtf_confirmation # Έλεγχος τάσης μεγαλύτερου timeframe (MTF)
from strategy.evaluate_indicators import evaluate_indicators # Απόφαση LONG ή SHORT με βάση δείκτες
from strategy.apply_indicators import apply_indicators # Υπολογισμός τεχνικών δεικτών
from strategy.trade_levels import calculate_trade_levels  # Υπολογισμός Entry, SL, TP
from chart_generator import generate_chart  # Δημιουργία γραφήματος με τα επίπεδα
from analyze_module.detailed_report import generate_detailed_report #σχετιζεται με τις πληροφοριες αναλυσης του ADMIN ΣΤΟΝ ΦΑΚΕΛΟ ANALYZE MODULE
from analyze_module.win_percent import calculate_win_percent # Να υπολογίσει πόσο πιθανό είναι ένα σήμα (LONG/SHORT) να πετύχει με βάση: τους τεχνικούς δείκτες (RSI, MACD, ADX, VWAP, OBV, TSI, POC κ.λπ.) και να δωσει ποσοστο % ΦΑΚΕΛΟ ANALYZE MODULE

# Ορισμός των καταστάσεων του ConversationHandler
SYMBOL, TIMEFRAME, LEVERAGE, RISK, CAPITAL, MTF = range(6)
# ID admin χρήστη για εμφάνιση πλήρους report
ADMIN_USER_IDS = [7316121101, 6721916403]   # Αντικατάστησέ το με το δικό σου ID

# Αρχή της συνομιλίας - ζητά symbol
async def analyze_start(update, context):
    await update.message.reply_text("🪙 Πληκτρολόγησε το symbol (π.χ. BTCUSDT):")
    return SYMBOL
# Λήψη symbol από τον χρήστη
async def receive_symbol(update, context):
    context.user_data["symbol"] = update.message.text.strip().upper()
    if not is_valid_symbol(context.user_data["symbol"]):
        await update.message.reply_text(
            f"❌ Το symbol `{context.user_data['symbol']}` δεν είναι έγκυρο.\n"
            f"👉 Βεβαιώσου ότι γράφεται π.χ. `BTCUSDT`, `ETHUSDT`, `SOLUSDT`.",
            parse_mode="Markdown"
        )
        return SYMBOL

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

