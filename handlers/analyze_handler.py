from telegram import Update, ReplyKeyboardRemove 
from telegram.ext import ( #για τις επιλογες που υπαρχουν στο tele π.χ(πληκτρολογησε το symbol. κλπ)
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from binance_utils import get_klines #για την ληψη των candlesticks #### Η get_klines() είναι μια Python συνάρτηση που δημιουργήσαμε για να τραβάει ιστορικά candlesticks (κεριά) από το Binance API.
from mtf_checker import check_mtf_confirmation #κανουμε import το αρχειο checker mtf για να υπαρχει η επιλογη mtf timeframe στην επιλογη /analyze
from evaluate_indicators import evaluate_indicators  #import σχεδιασμένο να αξιολογεί αυτόματα LONG ή SHORT σήματα με βάση όλους τους δείκτες ποιο αναλυτικα με αριθμους! περισσοτερες πληροφοριες στο evaluate indicators! ΕΙΝΑΙ STRATEGY
from apply_indicators import apply_indicators #import απο το αρχειο apple indicator για να παραγονται αυτοματα οι δεικτες στο signal 
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
    
    last = df.iloc[-1]
    indicators = {
            'rsi': last['RSI'],
            'macd_cross': last['MACD_Cross'],
            'macd_histogram': last['MACD_Hist'],
            'obv_trend': last['OBV_Trend'],
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

    signal = evaluate_indicators(indicators) #σχεδιασμένο να αξιολογεί αυτόματα LONG ή SHORT σήματα με βάση όλους τους δείκτες ποιο αναλυτικα με αριθμους! περισσοτερες πληροφοριες στο evaluate indicators! ΕΙΝΑΙ STRATEGY
    entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df, signal) #εφαρμοζει το entry stop loss tp1 tp2 απο αρχειο trade level με βάσει του σήματος LONG ή SHORT και του ATR.
    
    mtf_result = None
    if user_data.get("mtf") and user_data["mtf"].lower() != "skip":
        mtf_result = check_mtf_confirmation(symbol, user_data["mtf"], signal)

    conf_lines = [f"📢 Signal: {signal}", #σχετιζονατι με το αρχειο trade level 
                  f"🎯 Entry: {entry}",
                  f"🛑 SL: {sl}",
                  f"🎯 TP1: {tp1}",
                  f"🎯 TP2: {tp2}",
                  f"🎯 TP3: {tp3}",
                  f"\\n📊 Confirmations:"]

    for key, value in indicators.items(): #σχετιζεται με το evaluate_indicator
        conf_lines.append(f"- {key}: {val}")

    if mtf_result:
    conf_lines.append("\\n🧭 MTF Confirmation:") #αυτη η εντολη σχετιζεται με το confirmation που θα υπαρχει στην αναλυση για το mtf 
    for key, value in mtf_result.items():
        conf_lines.append(f"- {key}: {value}")

    response = "\n".join(conf_lines)
    chart = generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3)
    await update.message.reply_photo(photo=chart, caption=response, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
      
except Exception as e:
    await update.message.reply_text(f"❌ Σφάλμα κατά την ανάλυση: {str(e)}", reply_markup=ReplyKeyboardRemove())
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
