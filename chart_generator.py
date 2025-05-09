
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import io

def generate_chart(df, symbol, signal, entry, sl, tp1, tp2, tp3):
    df = df.tail(100)  # Πάρε τα τελευταία 100 candlesticks
    df['timestamp'] = df.index

    fig, ax = plt.subplots(figsize=(10, 5))

    # Candlesticks
    for i in range(len(df)):
        color = 'green' if df['close'].iloc[i] >= df['open'].iloc[i] else 'red'
        ax.plot([df['timestamp'].iloc[i], df['timestamp'].iloc[i]],
                [df['low'].iloc[i], df['high'].iloc[i]],
                color='black', linewidth=1)
        ax.add_patch(plt.Rectangle(
            (df['timestamp'].iloc[i], min(df['open'].iloc[i], df['close'].iloc[i])),
            width=0.01,
            height=abs(df['close'].iloc[i] - df['open'].iloc[i]),
            color=color
        ))

    # Επίπεδα Entry/SL/TPs
    ax.axhline(entry, color='blue', linestyle='--', linewidth=1, label='Entry')
    ax.axhline(sl, color='red', linestyle='--', linewidth=1, label='Stop Loss')
    ax.axhline(tp1, color='green', linestyle='--', linewidth=1, label='TP1')
    ax.axhline(tp2, color='green', linestyle='--', linewidth=1, label='TP2')
    ax.axhline(tp3, color='green', linestyle='--', linewidth=1, label='TP3')

    # Formatting
    ax.set_title(f"{symbol} {signal} Setup")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Αποθήκευση σε εικόνα bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf
