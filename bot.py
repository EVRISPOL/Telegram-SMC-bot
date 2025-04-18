import os
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ohlc import fetch_ohlc
from smc import detect_smc_signals
from indicators import check_indicators
from risk import calculate_risk_position
from chart import plot_trade_chart

OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))  # <-- YOUR TELEGRAM CHAT ID HERE

TOKEN = os.getenv("TELEGRAM_TOKEN")

VALID_TIMEFRAMES = ["1m", "3m", "5m", "15m", "30m", "1h", "4h"]

async def crypto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        command_parts = update.message.text[1:].split()  # remove "/" and split
        symbol = command_parts[0].upper() + "/USDT"
        timeframe = "3m"  # default

        if len(command_parts) > 1:
            tf_input = command_parts[1]
            if tf_input in VALID_TIMEFRAMES:
                timeframe = tf_input
            else:
                await update.message.reply_text(f"❌ Invalid timeframe: {tf_input}\nValid: {', '.join(VALID_TIMEFRAMES)}")
                return

        candles = fetch_ohlc(symbol, timeframe)
        smc = detect_smc_signals(candles)
        confirmation = check_indicators(candles)
        risk = calculate_risk_position(candles, smc['entry'], smc['sl'], capital=200)

        message = (
            f"**SMC Signal for {symbol}**\n"
            f"Timeframe: {timeframe}\n"
            f"Bias: {smc['bias']}\n\n"
            f"Entry: {smc['entry']}\n"
            f"Stop Loss: {smc['sl']}\n"
            f"TP1: {smc['tp1']}\n"
            f"TP2: {smc['tp2']}\n\n"
            f"Risk: {risk['risk_amount']}€\n"
            f"Entry Amount: {risk['position_size']} {symbol.split('/')[0]}\n"
            f"Indicators confirm: {confirmation['confirmed']}\n"
            f"Reasons: {', '.join(confirmation['reasons']) if not confirmation['confirmed'] else 'All conditions met'}"
        )

        
    alert, alert_reasons = check_alert_conditions(smc, confirmation)

    if alert:
        message = "🚨 *SMC ALERT*\n\n" + message
    else:
        message += f"\n\n⚠️ *No alert triggered:* {', '.join(alert_reasons)}"

    
    alert, alert_reasons = check_alert_conditions(smc, confirmation)

    if alert and update.effective_chat.id == OWNER_CHAT_ID:
        message = "🚨 *SMC ALERT*\n\n" + message
    elif not alert:
        message += f"\n\n⚠️ *No alert triggered:* {', '.join(alert_reasons)}"

    if alert and update.effective_chat.id == OWNER_CHAT_ID:
        log_alert('telegram-manual', symbol, timeframe, smc, '', '', '')
    await update.message.reply_text(message, parse_mode='Markdown')
    
    

        image_path = plot_trade_chart(candles, smc['entry'], smc['sl'], smc['tp1'], smc['tp2'], symbol=symbol, timeframe=timeframe)
        await update.message.reply_photo(photo=open(image_path, 'rb'))

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Διαχειριστής για πολλά symbols
    cryptos = ["btc", "eth", "xrp", "bnb", "sol", "ada", "doge", "matic", "dot", "link"]
    for crypto in cryptos:
        app.add_handler(CommandHandler(crypto, crypto_handler))

    print("Bot is running...")
    import asyncio
app.run_polling()
asyncio.create_task(auto_refresh_loop(app))

if __name__ == "__main__":
    main()


def check_alert_conditions(smc, indicators):
    reasons = []

    if not smc["liquidity_sweep"]:
        reasons.append("No liquidity sweep")
    if not smc["fvg_detected"]:
        reasons.append("No FVG")
    if smc["bias"] == "neutral":
        reasons.append("No clear bias")
    if not indicators["confirmed"]:
        reasons.append("Indicator mismatch")

    return len(reasons) == 0, reasons


import asyncio
import os

WATCHLIST = [
    ("BTC/USDT", "3m"),
    ("ETH/USDT", "5m"),
    ("XRP/USDT", "3m")
]

async def auto_refresh_loop(application):
    await application.bot.send_message(chat_id=OWNER_CHAT_ID, text="🔁 Auto-refresh started.")

    while True:
        for symbol, timeframe in WATCHLIST:
            try:
                candles = fetch_ohlc(symbol, timeframe)
                smc = detect_smc_signals(candles)
                confirmation = check_indicators(candles)
                alert, reasons = check_alert_conditions(smc, confirmation)

                if alert:
                    message = f"🚨 *Auto SMC ALERT*

"                               f"Symbol: {symbol}
Timeframe: {timeframe}
Bias: {smc['bias']}

"                               f"Entry: {smc['entry']}
SL: {smc['sl']}
TP1: {smc['tp1']}
TP2: {smc['tp2']}"
                    log_alert('telegram-auto', symbol, timeframe, smc, '', '', '')
        await application.bot.send_message(chat_id=OWNER_CHAT_ID, text=message, parse_mode='Markdown')

            except Exception as e:
                # Silent fail to keep loop alive
                print(f"[Auto-Refresh] Error for {symbol}: {e}")

        await asyncio.sleep(180)  # 3 minutes


import csv
from datetime import datetime


def log_alert(source, symbol, timeframe, smc, tp1_hit="", tp2_hit="", sl_hit=""):
    log_path = "logs/alerts.csv"
    log_exists = os.path.exists(log_path)
    os.makedirs("logs", exist_ok=True)

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow([
                "datetime", "source", "symbol", "timeframe",
                "bias", "entry", "sl", "tp1", "tp2",
                "sweep", "fvg", "tp1_hit", "tp2_hit", "sl_hit"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            source,
            symbol,
            timeframe,
            smc["bias"],
            smc["entry"],
            smc["sl"],
            smc["tp1"],
            smc["tp2"],
            smc["sweep_type"] if smc.get("liquidity_sweep") else "none",
            "yes" if smc.get("fvg_detected") else "no",
            tp1_hit,
            tp2_hit,
            sl_hit
        ])
