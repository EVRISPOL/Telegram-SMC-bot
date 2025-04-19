
import matplotlib.pyplot as plt
import pandas as pd

def plot_trade_chart(df, entry, sl, tp1, tp2, symbol="BTC/USDT", timeframe="3m", fvg_zone=None):
    fig, ax = plt.subplots(figsize=(12, 6))

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    for i in range(len(df)):
        color = 'green' if df['close'][i] >= df['open'][i] else 'red'
        ax.plot([df["timestamp"][i], df["timestamp"][i]], [df["low"][i], df["high"][i]], color=color)
        ax.plot([df["timestamp"][i], df["timestamp"][i]], [df["open"][i], df["close"][i]], color=color, linewidth=4)

    ax.axhline(entry, color='blue', linestyle='--', label=f"Entry: {entry}")
    ax.axhline(sl, color='red', linestyle='--', label=f"Stop Loss: {sl}")
    ax.axhline(tp1, color='green', linestyle='--', label=f"TP1: {tp1}")
    ax.axhline(tp2, color='green', linestyle='--', label=f"TP2: {tp2}")

    # Ασφαλής έλεγχος FVG
    if fvg_zone and isinstance(fvg_zone, tuple) and len(fvg_zone) == 2:
        top, bottom = fvg_zone
        ax.axhline(top, color='orange', linestyle=':', label="FVG Top")
        ax.axhline(bottom, color='orange', linestyle=':', label="FVG Bottom")

    ax.set_title(f"{symbol} Trade Setup ({timeframe})")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    image_path = "trade_chart.png"
    plt.savefig(image_path)
    plt.close()
    return image_path
