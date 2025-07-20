import requests
import time
import datetime
import json
from collections import defaultdict
from statistics import mean, stdev

ETHERSCAN_API_KEY = 'YourAPIKeyHere'
BASE_URL = 'https://api.etherscan.io/api'

# Кэш последних состояний кошельков
wallet_history = defaultdict(list)

def get_wallet_tx(wallet, startblock=0):
    """Получение списка транзакций для заданного кошелька"""
    url = f"{BASE_URL}?module=account&action=txlist&address={wallet}&startblock={startblock}&sort=asc&apikey={ETHERSCAN_API_KEY}"
    r = requests.get(url)
    data = r.json()
    if data["status"] != "1":
        return []
    return data["result"]

def detect_anomalies(wallet, tx_list):
    """Выявление аномалий на основе истории активности"""
    if len(tx_list) < 5:
        return None  # Мало данных

    times = [int(tx["timeStamp"]) for tx in tx_list]
    diffs = [j - i for i, j in zip(times[:-1], times[1:])]
    
    avg_diff = mean(diffs)
    std_diff = stdev(diffs) if len(diffs) > 1 else 0

    # Новые данные
    last_diff = int(time.time()) - times[-1]

    # Аномалия: долго спал, внезапно активен
    if last_diff < avg_diff - 2 * std_diff:
        return f"📈 Внезапное пробуждение кошелька {wallet}"

    # Аномалия: слишком часто отправляет
    if std_diff < 60 and avg_diff < 120:
        return f"💸 Частые транзакции — подозрительная активность у {wallet}"

    return None

def analyze_wallet(wallet):
    txs = get_wallet_tx(wallet)
    wallet_history[wallet].append(txs)
    result = detect_anomalies(wallet, txs)
    if result:
        print(f"[{datetime.datetime.now()}] {result}")

def main():
    watchlist = [
        "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",  # Пример кошелька
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    ]

    print("🧪 Cryptoscope — анализатор криптоаномалий")

    while True:
        for wallet in watchlist:
            try:
                analyze_wallet(wallet)
            except Exception as e:
                print(f"Ошибка с {wallet}: {e}")
        time.sleep(300)  # Пауза между циклами — 5 минут

if __name__ == "__main__":
    main()
