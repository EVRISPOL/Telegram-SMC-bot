import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from core import analyze_symbol  # import ανάλυσης

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📌 Your chat ID is: {update.effective_chat.id}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Usage: /symbol timeframe (e.g. /xrpusdt 3m)")
            return

        symbol = args[0].upper()
        timeframe = args[1]

        await update.message.reply_text(f"📊 Analyzing {symbol} on {timeframe}...")

        result = analyze_symbol(symbol, timeframe)
        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler(["xrp", "btc", "eth", "xrpusdt", "btcusdt", "ethusdt"], analyze))
    application.run_polling()
