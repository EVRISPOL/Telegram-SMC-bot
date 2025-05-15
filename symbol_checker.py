
import requests
import asyncio

valid_symbols = set()

def get_valid_binance_symbols():
    """Λήψη όλων των USDT συμβόλων από Binance"""
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    symbols = [
        s["symbol"] for s in data["symbols"]
        if s["status"] == "TRADING" and s["quoteAsset"] == "USDT"
    ]
    return set(symbols)

def is_valid_symbol(symbol: str) -> bool:
    """Έλεγχος αν το symbol υπάρχει στη λίστα"""
    return symbol.upper() in valid_symbols

async def refresh_symbol_list_every_hour():
    """Ανανέωση λίστας κάθε 1 ώρα"""
    global valid_symbols
    while True:
        try:
            valid_symbols = get_valid_binance_symbols()
            print(f"[Symbol Checker] Refreshed {len(valid_symbols)} symbols.")
        except Exception as e:
            print(f"[Symbol Checker] Error refreshing symbols: {e}")
        await asyncio.sleep(3600)  # 1 ώρα

def initialize_symbol_list():
    """Εκκίνηση με λήψη συμβόλων μία φορά"""
    global valid_symbols
    valid_symbols = get_valid_binance_symbols()
