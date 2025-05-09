from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from handlers.analyze_handler import get_analyze_handler #για τις επιλογες που υπαρχουν στην /analyze π.χ(πληκτρολογησε το symbol) 
from handlers.analyze_handler import analyze #για την εντολη /analyze απο handler analyze.py
from handlers.autosignal_handler import autosignal #για την εντολη /autosignal απο handler autosignal.py
from handlers.price_handler import price  #δεδομενα binance
from handlers.price_handler import price #για δεδομενα binance απο price handler
from config import BOT_TOKEN
from handlers.start_handler import start

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price)) #δεδομενα binance
    app.add_handler(CommandHandler("analyze", analyze)) #για την εντολη /analyze απο handler analyze.py
    app.add_handler(CommandHandler("autosignal", autosignal)) #για την εντολη /autosignal απο handler autosignal.py
    app.add_handler(get_analyze_handler()) #για τις επιλογες που υπαρχουν στην /analyze π.χ(πληκτρολογησε το symbol) 

    app.add_handler(CommandHandler("start", start))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
