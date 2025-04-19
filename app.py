
from flask import Flask, render_template, request, send_file
from ohlc import fetch_ohlc
from smc import detect_smc_signals
from indicators import check_indicators
from risk import calculate_risk_position
from chart import plot_trade_chart
from fpdf import FPDF
import csv
import os
from telegram import Bot

app = Flask(__name__)

# Ρύθμιση Telegram Bot
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

@app.route("/", methods=["GET", "POST"])
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

            # Ασφαλής διαχείριση FVG zone
            fvg_zone = smc.get("fvg_zone")
            if not (isinstance(fvg_zone, tuple) and len(fvg_zone) == 2):
                fvg_zone = None

            plot_trade_chart(candles, smc["entry"], smc["sl"], smc["tp1"], smc["tp2"],
                             symbol=symbol, timeframe=timeframe, fvg_zone=fvg_zone)

            signal = {
                "bias": smc["bias"],
                "entry": smc["entry"],
                "sl": smc["sl"],
                "tp1": smc["tp1"],
                "tp2": smc["tp2"]
            }

            # Αποστολή στο Telegram
            message = f"Signal: {signal['bias']} | Entry: {signal['entry']} | SL: {signal['sl']} | TP1: {signal['tp1']} | TP2: {signal['tp2']}"
            send_telegram_alert(message)

        except Exception as e:
            error = str(e)

        return render_template("index.html", signal=signal, error=error, symbol=symbol, timeframe=timeframe)

    return render_template("index.html")

@app.route("/download/png")
def download_png():
    return send_file("static/chart.png", as_attachment=True)

@app.route("/download/pdf")
def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SMC Signal Report", ln=True, align="C")
    pdf.ln(10)

    try:
        pdf.image("static/chart.png", x=10, y=30, w=180)
    except:
        pdf.cell(200, 10, txt="Chart image not found.", ln=True)

    pdf.output("static/report.pdf")
    return send_file("static/report.pdf", as_attachment=True)

@app.route("/history")
def history():
    alerts = []
    log_path = "logs/alerts.csv"
    filter_symbol = request.args.get("symbol", "")
    filter_bias = request.args.get("bias", "")

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (not filter_symbol or row["symbol"] == filter_symbol) and                    (not filter_bias or row["bias"] == filter_bias):
                    alerts.append(row)

    symbols = sorted(set(row["symbol"] for row in alerts))
    total = len(alerts)
    bullish = sum(1 for a in alerts if a["bias"] == "bullish")
    bearish = sum(1 for a in alerts if a["bias"] == "bearish")
    percent_bullish = round((bullish / total * 100), 1) if total else 0
    percent_bearish = round((bearish / total * 100), 1) if total else 0

    return render_template("history.html", alerts=alerts, filter_symbol=filter_symbol, filter_bias=filter_bias,
                           symbols=symbols, total=total, bullish=bullish, bearish=bearish,
                           percent_bullish=percent_bullish, percent_bearish=percent_bearish)

if __name__ == "__main__":
    app.run(debug=True)
