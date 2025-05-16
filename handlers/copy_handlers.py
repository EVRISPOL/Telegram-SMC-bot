
from telegram import Update
from telegram.ext import CallbackContext

async def handle_copy_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data  # example: 'copy_tp1_10429.9'
    parts = data.split("_", 2)

    if len(parts) == 3:
        label = parts[1].upper()
        value = parts[2]
        await query.message.reply_text(f"✅ Αντιγράφηκε: {label} = {value}")
