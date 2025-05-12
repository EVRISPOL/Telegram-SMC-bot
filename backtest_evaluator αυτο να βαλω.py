
import pandas as pd
from apply_indicators import apply_indicators
from evaluate_indicators import evaluate_indicators
from trade_levels import calculate_trade_levels

def run_backtest(file_path, symbol="BTCUSDT", timeframe="15m"):
    df = pd.read_csv(file_path)
    df = apply_indicators(df)

    results = []
    for i in range(30, len(df) - 10):  # από 30 για να έχουν υπολογιστεί όλοι οι δείκτες
        row = df.iloc[i]
        indicators = {
            'rsi': row['RSI'],
            'macd_cross': row['MACD_Cross'],
            'macd_histogram': row['MACD_Hist'],
            'obv_trend': row['OBV_Trend'],
            'vwap': row['VWAP'],
            'price': row['close'],
            'ema_trend': row['EMA_Trend'],
            'atr': row['ATR'],
            'atr_sma': df['ATR'].rolling(14).mean().iloc[i],
            'bollinger_breakout': row['Boll_Breakout'],
            'stochrsi_k': row['StochRSI_K'],
            'stochrsi_d': row['StochRSI_D'],
            'adx': row['adx']
        }

        direction = evaluate_indicators(indicators)
        if direction in ['LONG', 'SHORT']:
            entry, sl, tp1, tp2, tp3 = calculate_trade_levels(df.iloc[:i+1], direction)

            reached = "NONE"
            for j in range(1, 10):
                future = df.iloc[i + j]
                price = future['high'] if direction == "LONG" else future['low']
                if direction == "LONG":
                    if price >= tp3:
                        reached = "TP3"; break
                    elif price >= tp2:
                        reached = "TP2"
                    elif price >= tp1:
                        reached = "TP1"
                    elif future['low'] <= sl:
                        reached = "SL"; break
                else:
                    if price <= tp3:
                        reached = "TP3"; break
                    elif price <= tp2:
                        reached = "TP2"
                    elif price <= tp1:
                        reached = "TP1"
                    elif future['high'] >= sl:
                        reached = "SL"; break

            results.append(reached)

    # Αποτελέσματα
    total = len(results)
    tp1 = results.count("TP1")
    tp2 = results.count("TP2")
    tp3 = results.count("TP3")
    sl = results.count("SL")
    wins = tp1 + tp2 + tp3
    win_rate = round((wins / total) * 100, 2) if total > 0 else 0

    print(f"Backtest για {symbol} ({timeframe})")
    print(f"Signals: {total}")
    print(f"TP1: {tp1}, TP2: {tp2}, TP3: {tp3}, SL: {sl}")
    print(f"Success Rate: {win_rate}%")

if __name__ == "__main__":
    files = [
        ("BTCUSDT_3m.csv", "BTCUSDT", "3m"),
        ("BTCUSDT_5m.csv", "BTCUSDT", "5m"),
        ("BTCUSDT_15m_sample.csv", "BTCUSDT", "15m")
    ]

    for file_path, symbol, tf in files:
        print("=" * 40)
        run_backtest(file_path, symbol, tf)
