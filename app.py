
test_mode = True  # True for Test Mode, False for real execution

# Modify the analyze_trade function to implement the Test Mode behavior
def analyze_trade(symbol, time_frame):
    if test_mode:
        print(f"Test Mode: Analyzing {symbol} on {time_frame}...")
        # Add detailed analysis output in Test Mode
        print("✔ BOS detected (Break of Structure)")
        print(f"✔ Order Block (OB) found at level 1.235")
        print(f"✔ MACD shows bullish trend")
        print(f"✖ RSI not in optimal range (current: {current_rsi})")
        
        # Simulate the result of no valid setup in Test Mode
        return "No valid SMC setup found for Test Mode"
    
    else:
        # This is where the normal logic for live trading would go
        pass

# Update send_message to include Test Mode behavior
def send_message(chat_id, message):
    if test_mode:
        # Send detailed analysis to Telegram in Test Mode
        bot.send_message(chat_id, f"Test Mode: {message}")
    else:
        # Normal message in live trading mode
        bot.send_message(chat_id, message)
