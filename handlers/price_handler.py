
import requests
from telegram import Update
from telegram.ext import ContextTypes

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗ Χρήση: /price BTCUSDT")
        return

    symbol = context.args[0].upper()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    try:
        response = requests.get(url)
        data = response.json()
        price = data.get("price")

        if price:
            await update.message.reply_text(f"💱 Τιμή {symbol}: {price} USDT")
        else:
            await update.message.reply_text("⚠️ Δεν βρέθηκε το symbol ή υπήρξε σφάλμα.")
    except Exception as e:
        await update.message.reply_text(f"❌ Σφάλμα: {str(e)}")
