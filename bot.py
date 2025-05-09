from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN
from handlers.start_handler import start

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
