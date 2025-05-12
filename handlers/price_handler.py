# Εισαγωγή requests για HTTP αιτήματα και Telegram components για απαντήσεις στο bot
import requests
from telegram import Update
from telegram.ext import ContextTypes
# Συνάρτηση για την εντολή /price
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗ Χρήση: /price BTCUSDT")
        return
    # Ανάγνωση του symbol και μετατροπή σε κεφαλαία
    symbol = context.args[0].upper()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

    try:   # Κλήση του Binance API για να πάρουμε την τιμή
        response = requests.get(url)
        data = response.json()
        price = data.get("price")
        # Αν υπάρχει τιμή, στείλε την στον χρήστη
        if price:
            await update.message.reply_text(f"💱 Τιμή {symbol}: {price} USDT")
        else:  # Αν δεν βρέθηκε τιμή ή υπήρξε πρόβλημα
            await update.message.reply_text("⚠️ Δεν βρέθηκε το symbol ή υπήρξε σφάλμα.")
    except Exception as e:  # Αν προκύψει εξαίρεση κατά την κλήση του API
        await update.message.reply_text(f"❌ Σφάλμα: {str(e)}")
