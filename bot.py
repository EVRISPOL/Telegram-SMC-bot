
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Your chat ID is: {chat_id}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split()
        if len(parts) < 2:
            await update.message.reply_text("❗Usage: /symbol timeframe (e.g. /xrp 3m)")
            return
        symbol = parts[0][1:].upper()
        timeframe = parts[1]

        pair = symbol + "USDT"
        await update.message.reply_text(f"📊 Analyzing {symbol} on {timeframe}...")

        klines = client.get_klines(symbol=pair, interval=timeframe, limit=100)
        if not klines:
            await update.message.reply_text(f"❌ Error: No data found for {pair} with timeframe {timeframe}")
            return

        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        df = df.astype(float)

        # Basic trend analysis example
        last_close = df["close"].iloc[-1]
        prev_close = df["close"].iloc[-2]
        direction = "📈 Uptrend" if last_close > prev_close else "📉 Downtrend"

        await update.message.reply_text(
            f"{symbol} on {timeframe}:
Last Close: {last_close:.4f}
Prev Close: {prev_close:.4f}
{direction}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(None, analyze))  # handle all other commands
    app.run_polling()
