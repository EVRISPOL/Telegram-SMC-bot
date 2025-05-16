from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup ### ΣΕ ΑΥΤΟ ΤΟ ΑΡΧΕΙΟ ΒΡΙΣΚΟΝΤΑΙ ΤΑ ΚΟΥΜΠΙΑ COPY ΣΤΗΝ /ANALYZE ΠΟΥ ΕΜΦΑΝΙΖΟΝΤΑΙ ΔΙΠΛΑ ΑΠΟ ENTRY/SL/TP1/TP2 ΚΛΠ
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

def generate_copy_keyboard(entry, sl, tp1, tp2, tp3, profit_tp1, profit_tp2, profit_tp3, symbol):
    keyboard = [
        [
            InlineKeyboardButton(f"📥 Entry: {entry}", callback_data="none"),
            InlineKeyboardButton("📋", callback_data=f"copy_entry_{entry}")
        ],
        [
            InlineKeyboardButton(f"❌ Stop Loss: {sl}", callback_data="none"),
            InlineKeyboardButton("📋", callback_data=f"copy_sl_{sl}")
        ],
        [
            InlineKeyboardButton(f"🟢 TP1: {tp1} (+{profit_tp1}€)", callback_data="none"),
            InlineKeyboardButton("📋", callback_data=f"copy_tp1_{tp1}")
        ],
        [
            InlineKeyboardButton(f"🟡 TP2: {tp2} (+{profit_tp2}€)", callback_data="none"),
            InlineKeyboardButton("📋", callback_data=f"copy_tp2_{tp2}")
        ],
        [
            InlineKeyboardButton(f"🔴 TP3: {tp3} (+{profit_tp3}€)", callback_data="none"),
            InlineKeyboardButton("📋", callback_data=f"copy_tp3_{tp3}")
        ],
        [
            InlineKeyboardButton("📊 Στοιχεία", callback_data="show_details")
        ],
        [
            InlineKeyboardButton("📈 Δες στο TradingView", url=f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}")
        ],
        [
            InlineKeyboardButton("📤 Εκτέλεση στο Bybit", url=f"https://www.bybit.com/en-US/trade/usdt/{symbol}")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

