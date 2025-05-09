from telegram import Update, ReplyKeyboardRemove 
from telegram.ext import ( #για τις επιλογες που υπαρχουν στο tele π.χ(πληκτρολογησε το symbol. κλπ)
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from binance_utils import get_klines #για την ληψη των candlesticks #### Η get_klines() είναι μια Python συνάρτηση που δημιουργήσαμε για να τραβάει ιστορικά candlesticks (κεριά) από το Binance API.
from analyze_indicators import apply_indicators #import απο το αρχειο analyze indicator για να παραγονται αυτοματα οι δεικτες στο signal 
from signal_decision import decide_signal #import απο το αρχειο signal_decision = υπολογιζει αυτοματα στην αναλυση long/short
from trade_levels import calculate_trade_levels #import απο το αρχειο trade levels = υπολογισμος stop loss tp1 tp2 tp3! 
from chart_generator import generate_chart #import απο το chart generator για την εμφανιση εικονας chart στην ολοκληρωση της αναλυσης

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
    df = get_klines(symbol, interval=timeframe) #φέρνει τα candlesticks από Binance
    df = apply_indicators(df) #εφαρμόζει όλους τους δείκτες πάνω στο dataframe (RSI, MACD, VWAP, ATR, κ.λπ.)
    signal, confirmations = decide_signal(df) #Εξετάζει το τελευταίο candlestick και στην συνεχεια δινει τα confirmation στους δεικτες
    entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df, signal) #εφαρμοζει το entry stop loss tp1 tp2 απο αρχειο trade level με βάσει του σήματος LONG ή SHORT και του ATR.

    conf_lines = [f"📢 Signal: {signal}", #σχετιζονατι με το αρχειο trade level 
                  f"🎯 Entry: {entry}",
                  f"🛑 SL: {sl}",
                  f"🎯 TP1: {tp1}",
                  f"🎯 TP2: {tp2}",
                  f"🎯 TP3: {tp3}",
                  f"\\n📊 Confirmations:"]
    for key, value in confirmations.items():
        if value == "LONG":
            icon = "✅ LONG"
        elif value == "SHORT":
            icon = "🔻 SHORT"
        elif value == "NONE":
            icon = "✅ NONE"
        else:
            icon = f"🔸 {value}"
        conf_lines.append(f"- {key}: {icon}")
        
        response = "\n".join(conf_lines)
    except Exception as e:
        response = f"❌ Σφάλμα κατά την ανάλυση: {str(e)}"

    chart = generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3)  #import απο το chart generator για την εμφανιση εικονας chart στην ολοκληρωση της αναλυσης
    await update.message.reply_photo(photo=chart, caption=response, reply_markup=ReplyKeyboardRemove())
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
