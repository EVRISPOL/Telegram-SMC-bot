
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from ohlc import fetch_ohlc
from smc import detect_smc_signals
from indicators import check_indicators
from risk import calculate_risk_position
from chart import plot_trade_chart

OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CAPITAL = float(os.getenv("CAPITAL", "200"))
DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "3m")
RISK_PERCENT = float(os.getenv("RISK_PERCENT", "2"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your chat ID is: {update.effective_chat.id}")

async def crypto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) == 0:
            await update.message.reply_text("Please provide symbol and optionally timeframe. E.g. /xrp 3m")
            return

        symbol = update.message.text.split()[0][1:].upper()
        timeframe = args[0] if len(args) > 0 else DEFAULT_TIMEFRAME

        ohlc = fetch_ohlc(symbol, timeframe)
        smc_data = detect_smc_signals(ohlc)
        if not smc_data.get("entry"):
            await update.message.reply_text("No valid SMC setup found.")
            return

        indicators_ok, reasons = check_indicators(ohlc)
        if not indicators_ok:
            await update.message.reply_text("Signal rejected by indicators: " + ", ".join(reasons))
            return

        risk_data = calculate_risk_position(CAPITAL, RISK_PERCENT, smc_data["entry"], smc_data["stop_loss"])
        chart_path = plot_trade_chart(ohlc, smc_data)

        message = (
            "SMC Analysis\n"
            f"Symbol: {symbol}\n"
            f"Timeframe: {timeframe}\n"
            f"Bias: {smc_data['bias']}\n"
            f"Entry: {smc_data['entry']}\n"
            f"SL: {smc_data['stop_loss']}\n"
            f"TP1: {smc_data['tp1']}\n"
            f"TP2: {smc_data['tp2']}\n"
            f"Position Size: {risk_data['position_size']} ({RISK_PERCENT}% of {CAPITAL})\n\n"
            "Indicators: Confirmed"
        )

        await update.message.reply_photo(photo=open(chart_path, "rb"), caption=message)
    except Exception as e:
        logger.error(f"Error in crypto_handler: {e}")
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("xrp", crypto_handler))
    application.add_handler(CommandHandler("btc", crypto_handler))
    application.add_handler(CommandHandler("eth", crypto_handler))
    application.add_handler(CommandHandler("sol", crypto_handler))
    application.run_polling()
