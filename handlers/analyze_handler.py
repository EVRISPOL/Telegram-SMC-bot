from telegram import Update, ReplyKeyboardRemove 
from analyze_indicators import apply_indicators #import απο το αρχειο analyze indicator για να παραγονται αυτοματα οι δεικτες στο signal 
from telegram.ext import ( #για τις επιλογες που υπαρχουν στο tele π.χ(πληκτρολογησε το symbol. κλπ)
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from binance_utils import get_klines #για την ληψη των candlesticks #### Η get_klines() είναι μια Python συνάρτηση που δημιουργήσαμε για να τραβάει ιστορικά candlesticks (κεριά) από το Binance API.

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Εδώ θα υλοποιηθεί η λογική για την εντολή /analyze
    pass

# Βήματα
SYMBOL, TIMEFRAME, LEVERAGE, RISK, CAPITAL, MTF = range(6)

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
    context.user_data["mtf"] = update.message.text.strip()
   
 # Λήψη candlesticks από Binance
    symbol = context.user_data["symbol"]
    timeframe = context.user_data["timeframe"]
    
    try:
        df = get_klines(symbol, interval=timeframe, limit=100)
        response = (
            f"✅ Λήψη candlesticks επιτυχής για {symbol} ({timeframe})
"
            f"📊 Εγγραφές: {len(df)}"
        )
    except Exception as e:
        response = f"❌ Σφάλμα κατά τη λήψη δεδομένων: {str(e)}"

    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

    await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove())
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
