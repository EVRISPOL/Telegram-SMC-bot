from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import CallbackQueryHandler

from symbol_checker import initialize_symbol_list            # ελεγχος εγκυρης πληκτρολογησης signal απο symbol checker!
from handlers.analyze_handler import show_details_callback   # Callback για εμφάνιση αναλυτικού report
from handlers.analyze_handler import get_analyze_handler     # Handler για τη ροή εντολής /analyze (symbol, timeframe, capital κ.λπ.)
from handlers.autosignal_handler import autosignal           # Συνάρτηση που στέλνει αυτόματα signals (/autosignal)
from handlers.price_handler import price                     # Συνάρτηση που απαντά με την τρέχουσα τιμή (/price)
from config import BOT_TOKEN                                 # Το token του bot από αρχείο config
from handlers.start_handler import start                     # Συνάρτηση για το /start μήνυμα
from handlers.copy_handlers import handle_copy_button                 # Σε αυτο το αρχειο βρισκονται τα κουμπια copy που εμφανιζονται διπλα απο το entry/sl/tp1 κλπ!

 # 🚀 Κύρια συνάρτηση που ξεκινάει το bot
def main():
    initialize_symbol_list()  # ✅ Λήψη Binance symbols μία φορά κατά την εκκίνηση

     # Δημιουργία εφαρμογής με το BOT_TOKEN
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # 💰 Εντολή /price – Επιστρέφει την τρέχουσα τιμή από Binance
    app.add_handler(CommandHandler("price", price)) 
    # 📡 Εντολή /autosignal – Στέλνει αυτόματα ανιχνευμένα σήματα αγοράς
    app.add_handler(CommandHandler("autosignal", autosignal))
    # 🧠 Εντολή /analyze – Εκκίνηση ροής ανάλυσης (symbol, timeframe, leverage, κ.λπ.)
    app.add_handler(get_analyze_handler())
    # ℹ️ Callback όταν πατηθεί το κουμπί "Στοιχεία" για εμφάνιση πλήρους ανάλυσης (μόνο admin)
    app.add_handler(CallbackQueryHandler(show_details_callback, pattern="show_details"))
    # 👋 Εντολή /start – Καλωσόρισμα του χρήστη
    app.add_handler(CommandHandler("start", start))
    # Σε αυτο το αρχειο βρισκονται τα κουμπια copy που εμφανιζονται διπλα απο το entry/sl/tp1 κλπ!
    app.add_handler(CallbackQueryHandler(handle_copy_button, pattern=r'^copy_'))
     # ✅ Μήνυμα επιβεβαίωσης ότι το bot τρέχει
    print("✅ Bot is running...")
    app.run_polling()
# Αν το αρχείο τρέχει ως main script, ξεκίνα το bot
if __name__ == "__main__":
    main()
