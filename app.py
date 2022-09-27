"""Crypto Interview Assessment Module."""

import logging
import time
from datetime import datetime

from dotenv import find_dotenv, load_dotenv

import crypto_api
from db import get_transaction_history, initialize_db, upsert_crypto

logging.basicConfig(
    level=logging.DEBUG,
    filename="storage/logs/app.log",
    format="%(asctime)s %(levelname)s:%(message)s",
)
load_dotenv(find_dotenv(raise_error_if_not_found=False))

initialize_db()


def cron_job():
    # Phase 1
    coins = crypto_api.get_coins()
    # Storing top 3 coins (by current market cap)
    first_coin, second_coin, third_coin = coins[0:3]
    upsert_crypto(first_coin)
    upsert_crypto(second_coin)
    upsert_crypto(third_coin)

    # Phase 2
    # Fetching 10 day average for the top 3 cryptocurrencies
    first_coin_avg = get_10_day_average(first_coin.get("id"))
    second_coin_avg = get_10_day_average(second_coin.get("id"))
    third_coin_avg = get_10_day_average(third_coin.get("id"))

    print(
        f"===================== Purchase made at {datetime.now()} ====================="
    )
    if first_coin.get("current_price") < first_coin_avg:
        crypto_api.submit_order(
            first_coin.get("id"), 1, first_coin.get("current_price")
        )
    if second_coin.get("current_price") < second_coin_avg:
        crypto_api.submit_order(
            second_coin.get("id"), 1, second_coin.get("current_price")
        )
    if third_coin.get("current_price") < third_coin_avg:
        crypto_api.submit_order(
            third_coin.get("id"), 1, third_coin.get("current_price")
        )

    calculate_portfolio(coins)


def get_10_day_average(coin_id: str) -> float:
    history = crypto_api.get_coin_price_history(coin_id)
    sum = 0
    for (_, price) in history:
        sum += price
    return sum / 10


def calculate_portfolio(coins):
    current_price_map = {x["id"]: x["current_price"] for x in coins}
    transactions = get_transaction_history()

    portfolio_map = {}
    for transaction in transactions:
        if transaction[0] not in portfolio_map:
            portfolio_map[transaction[0]] = [1, transaction[2]]
        else:
            portfolio_map[transaction[0]] = [
                portfolio_map[transaction[0]][0] + 1,
                portfolio_map[transaction[0]][1] + transaction[2],
            ]

    logging.debug(
        "===================== Printing results of current portfolio ====================="
    )
    print(
        "===================== Printing results of current portfolio ====================="
    )

    for coin_id, (count, total_purchase_price) in portfolio_map.items():
        logging.debug(
            f"ID: {coin_id} | Buy count: {count} | Loss/gain: {calculate_loss_gain(total_purchase_price, current_price_map[coin_id] * count)}"
        )
        print(
            f"ID: {coin_id} | Buy count: {count} | Loss/gain: {calculate_loss_gain(total_purchase_price, current_price_map[coin_id] * count)}"
        )


def calculate_loss_gain(purchase_price, current_price):
    return f"{round(((current_price - purchase_price) / purchase_price * 100), 2)} %"


while True:
    cron_job()
    time.sleep(3600)  # Adjust this to a lesser number for testing purposes
