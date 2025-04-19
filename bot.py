
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from ohlc import fetch_ohlc
from smc import detect_smc_signals
from indicators import check_indicators
from risk import calculate_risk_position
from chart import plot_trade_chart

# .env μεταβλητές
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CAPITAL = float(os.getenv("CAPITAL", "200"))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", "2"))
DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "3m")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text(f"✅ Bot is running. Your chat ID is: {update.effective_chat.id}")

# /symbol [timeframe]
async def analyze_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
	try:
		parts = update.message.text.strip().split()
		if len(parts) < 1:
			await update.message.reply_text("❗ Format: /symbol [timeframe]. Example: /xrp 3m")
			return

		symbol = parts[0][1:].upper()
		timeframe = parts[1] if len(parts) > 1 else DEFAULT_TIMEFRAME

		await update.message.reply_text(f"📊 Analyzing {symbol} on {timeframe}...")

		ohlc = fetch_ohlc(symbol, timeframe)
		smc_data = detect_smc_signals(ohlc)

		if not smc_data.get("entry"):
			await update.message.reply_text("⚠️ No valid SMC setup found.")
			return

		indicator_result = check_indicators(ohlc)
		if not indicator_result["confirmed"]:
			await update.message.reply_text("❌ Rejected by indicators: " + ", ".join(indicator_result["reasons"]))
			return

		risk_data = calculate_risk_position(ohlc, smc_data["entry"], smc_data.get("sl", smc_data["entry"] * 0.98))
		chart_path = plot_trade_chart(
			ohlc,
			smc_data["entry"],
			smc_data.get("sl", smc_data["entry"] * 0.98),
			smc_data.get("tp1", smc_data["entry"] * 1.02),
			smc_data.get("tp2", smc_data["entry"] * 1.04),
			symbol=f"{symbol}/USDT",
			timeframe=timeframe,
			fvg_zone=smc_data.get("fvg_zone")
		)

		message = (
			f"Score: {smc_data['score']}
"
			f"Sweep: {smc_data['sweep']}
"
			f"FVG Zone: {smc_data['fvg_zone']}
"
			f"SMC Analysis for {symbol} ({timeframe})
"
			f"Bias: {smc_data['bias']}
"
			f"Entry: {smc_data['entry']}
"
			f"Stop Loss: {smc_data.get('sl', smc_data['entry'] * 0.98)}
"
			f"TP1: {smc_data.get('tp1', smc_data['entry'] * 1.02)}
"
			f"TP2: {smc_data.get('tp2', smc_data['entry'] * 1.04)}
"
			f"Position Size: {risk_data['position_size']} ({RISK_PERCENT}% of {CAPITAL})
"
			f"Indicators: Confirmed"
		)

		with open(chart_path, "rb") as chart_file:
			await update.message.reply_photo(photo=chart_file, caption=message)
	except Exception as e:
		logger.error(f"Error in analyze_handler: {e}")
		await update.message.reply_text(f"❌ Error: {str(e)}")

if __name__ == "__main__":
	application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
	application.add_handler(CommandHandler("start", start_handler))

	symbols = ["xrp", "btc", "eth", "sol", "doge", "ada", "link", "matic", "avax", "bnb"]
	for sym in symbols:
		application.add_handler(CommandHandler(sym, analyze_handler))

	application.run_polling()
