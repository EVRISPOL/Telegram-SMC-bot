from flask import Flask, render_template, request
from ohlc import fetch_ohlc
from smc import detect_smc_signals
from indicators import check_indicators
from risk import calculate_risk_position
from chart import plot_trade_chart
import os

app = Flask(__name__)

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
            plot_trade_chart(candles, smc["entry"], smc["sl"], smc["tp1"], smc["tp2"], symbol=symbol, timeframe=timeframe, fvg_zone=smc.get("fvg_zone"))

            signal = {
                "bias": smc["bias"],
                "entry": smc["entry"],
                "sl": smc["sl"],
                "tp1": smc["tp1"],
                "tp2": smc["tp2"]
            }
        except Exception as e:
            error = str(e)

        return render_template("index.html", signal=signal, error=error, symbol=symbol, timeframe=timeframe)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


from flask import send_file
from fpdf import FPDF

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


import csv
from flask import send_file, render_template


from flask import request

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
