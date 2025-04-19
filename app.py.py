
from telegram import Bot

# Set your Telegram bot token here
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_alert(message):
    chat_id = 'YOUR_CHAT_ID'  # Set the chat ID here
    bot.send_message(chat_id=chat_id, text=message)

def index():
    signal = None
    error = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        timeframe = request.form["timeframe"]
        try:
            candles = fetch_ohlc(symbol, timeframe)
            smc = detect_smc_signals(candles)
            confirmation = check_indicators(candles)
            rsi_value = confirmation['rsi']
            macd_value = confirmation['macd']
            volume = confirmation['volume']
            confirmed = confirmation['confirmed']
            risk = calculate_risk_position(candles, smc['entry'], smc['sl'], capital=200)
            plot_trade_chart(candles, smc["entry"], smc["sl"], smc["tp1"], smc["tp2"], symbol=symbol, timeframe=timeframe, fvg_zone=smc.get("fvg_zone"))

            signal = {
                "bias": smc["bias"],
                "entry": smc["entry"],
                "sl": smc["sl"],
                "tp1": smc["tp1"],
                "tp2": smc["tp2"]
            }

            # Sending signal to Telegram
            message = f"Signal: {signal['bias']} | Entry: {signal['entry']} | SL: {signal['sl']} | TP1: {signal['tp1']} | TP2: {signal['tp2']}"
            send_telegram_alert(message)  # Send the signal as an alert to Telegram

        except Exception as e:
            error = str(e)

        return render_template("index.html", signal=signal, error=error, symbol=symbol, timeframe=timeframe)

    return render_template("index.html")
