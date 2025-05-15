from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from binance_utils import get_klines
from strategy.apply_indicators import apply_indicators
from strategy.evaluate_indicators import evaluate_indicators
from strategy.trade_levels import calculate_trade_levels
from strategy.mtf_checker import check_mtf_confirmation
from chart_generator import generate_chart

from analyze_module.win_percent import calculate_win_percent
from analyze_module.detailed_report import generate_detailed_report

async def finalize_analysis(update, context):
    try:
        user_data = context.user_data
        symbol = user_data["symbol"]
        timeframe = user_data["timeframe"]
        df = get_klines(symbol, interval=timeframe)
        df = apply_indicators(df)
        last = df.iloc[-1]

        indicators = {
            'rsi': last['RSI'],
            'macd_cross': last['MACD_Cross'],
            'macd_histogram': last['MACD_Hist'],
            'obv_trend': last['OBV_Trend'],
            'obv': last['OBV'],
            'price': last['close'],
            'vwap': last['VWAP'],
            'ema_trend': last['EMA_Trend'],
            'atr': last['ATR'],
            'atr_sma': df['ATR'].rolling(14).mean().iloc[-1],
            'bollinger_breakout': last['Boll_Breakout'],
            'stochrsi_k': last['StochRSI_K'],
            'stochrsi_d': last['StochRSI_D'],
            'adx': last['adx'],
            'tsi': last['TSI'],
            'poc': last['POC'],
            'candle_pattern': last['candle_pattern'],
        }

        signal = evaluate_indicators(indicators)
        entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df, signal)

        indicators.update({
            'volume': last['volume'],
            'avg_volume': df['volume'].rolling(20).mean().iloc[-1],
            'tp1': tp1,
            'atr': last['ATR'],
            'swing_high': last['swing_high'],
            'swing_low': last['swing_low'],
        })

        win_percent, confirmations = calculate_win_percent(indicators, signal)
        confirmation_count = sum(1 for v in confirmations.values() if v)
        total_confirmations = len(confirmations)

        mtf_result = None
        if user_data.get("mtf") and user_data["mtf"].lower() != "skip":
            mtf_result = check_mtf_confirmation(symbol, user_data["mtf"], signal)

        capital = float(user_data["capital"])
        risk = float(user_data["risk"])
        leverage = float(user_data["leverage"])
        position_size = capital * leverage
        risk_amount = round(capital * (risk / 100), 2)

        def calculate_profit(entry, target, size):
            return round((size * (target - entry) / entry), 2)

        profit_tp1 = calculate_profit(entry, tp1, position_size)
        profit_tp2 = calculate_profit(entry, tp2, position_size)
        profit_tp3 = calculate_profit(entry, tp3, position_size)

        response = (
            f"📢 Signal: {signal}\n"
            f"🎯 Entry: {entry}\n\n"
            f"🛑 SL: {sl}\n\n"
            f"🎯 TP1: {tp1}  (+{profit_tp1}€)\n"
            f"🎯 TP2: {tp2}  (+{profit_tp2}€)\n"
            f"🎯 TP3: {tp3}  (+{profit_tp3}€)\n\n"
            f"💸 Μέγιστη ζημία (SL): -{risk_amount}€\n"
            f"✅ Confirmations: {confirmation_count} / {total_confirmations}\n"
            f"📊 MTF Trend: {'✅ Συμφωνία' if mtf_result else '❌ Διαφωνία'}\n\n"
            f"🎯 AI WIN Prediction:\n\n"
            f"• TP1: {round(win_percent, 1)}%\n"
            f"• TP2: {round(max(win_percent - 10, 0), 1)}%\n"
            f"• TP3: {round(max(win_percent - 20, 0), 1)}%\n"
            f"• SL: {round(100 - win_percent, 1)}%"
        )

        keyboard = [[InlineKeyboardButton("ℹ️ Στοιχεία", callback_data="show_details")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        chart = generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3)
        context.user_data['full_analysis'] = generate_detailed_report(indicators, signal, win_percent, mtf_result if mtf_result is not None else True)

        await update.message.reply_photo(photo=chart, caption=response, reply_markup=reply_markup)
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"❌ Σφάλμα κατά την ανάλυση: {str(e)}", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
