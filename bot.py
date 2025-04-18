from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ohlc import fetch_ohlc
from smc import detect_smc_signals
from indicators import check_indicators
from risk import calculate_risk_position

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def handle_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = update.message.text.replace("/", "").upper() + "/USDT"
        timeframe = "3m"

        candles = fetch_ohlc(symbol, timeframe)
        smc = detect_smc_signals(candles)
        confirmation = check_indicators(candles)
        risk = calculate_risk_position(candles, smc['entry'], smc['sl'], capital=200)

        message = (
            f"**SMC Signal for {symbol}**\n"
            f"Timeframe: {timeframe}\n\n"
            f"Entry: {smc['entry']}\n"
            f"Stop Loss: {smc['sl']}\n"
            f"TP1: {smc['tp1']}\n"
            f"TP2: {smc['tp2']}\n\n"
            f"Risk: {risk['risk_amount']}€\n"
            f"Entry Amount: {risk['position_size']} {symbol.split('/')[0]}\n"
            f"Indicators confirm: {confirmation['confirmed']}"
        )

        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("btc", handle_crypto))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
