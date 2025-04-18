import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from smc import detect_smc_signals

import os

TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send /xrp to get SMC signal.")

async def xrp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signal = detect_smc_signals("XRP/USDT", timeframe="3m")
    await update.message.reply_text(signal)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("xrp", xrp))
    app.run_polling()
