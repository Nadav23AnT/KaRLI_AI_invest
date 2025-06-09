import os
import time
import requests
import yfinance as yf
import logging

from alpacaTrading import create_client
from alpacaTrading.account import submit_order, get_client_position
from mongo_utils import get_all_users_with_credentials

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Fetch Market Data from Yahoo (if needed) ---
def handle_new_market_data(tickers):
    print("handle_new_market_data")
    # data = yf.download(tickers=tickers, period="1d", interval="1d")
    # return data


# --- Query Model API for Action Predictions ---
def get_ticker_actions():
    try:
        response = requests.post("http://localhost:8000/get-actions")
        response.raise_for_status()
        return response.json()  # e.g., {"AAPL": 1, "TSLA": 3}
    except Exception as e:
        logger.error("Failed to fetch ticker actions: %s", e)
        return {}


# --- Send Orders to Alpaca ---
def send_order_to_alpaca(api_key, api_secret, symbol, action):
    client = create_client("api_key", "api_secret")

    try:

        if action == 1:  # Buy
            submit_order(client, symbol, 1, "buy", "market", "day")
            logger.info("[ORDER] Buy %s", symbol)

        elif action == 3:  # Sell
            try:
                position = get_client_position(client, symbol)

                if position:
                    submit_order(client, symbol, position.qty, "sell", "market", "day")
                    logger.info("[ORDER] Sell %s", symbol)
            except Exception as e:
                logger.info("[SKIP] No position to sell for %s", symbol)
        else:  # Hold
            logger.info("[HOLD] %s", symbol)
    except Exception as e:
        logger.error("[ERROR] Order failed for %s: %s", symbol, e)


# --- Main Scheduled Logic ---
def daily_task():
    logger.info("[START] Daily trading task")
    actions = get_ticker_actions()
    if not actions:
        logger.info("[INFO] No actions received.")
        return

    users = get_all_users_with_credentials()
    for user in users:
        username = user["username"]
        risk = user["risk"]
        api_key = user["api_key"]
        api_secret = user["api_secret"]

        if not api_key or not api_secret:
            logger.warning("[SKIP] Missing Alpaca credentials for %s", username)
            continue

        logger.info("[USER] %s - Risk: %s", username, risk)
        for ticker, action in actions.items():
            logger.info("[ACTION] %s: %s", ticker, ["", "BUY", "HOLD", "SELL"][action])
            send_order_to_alpaca(api_key, api_secret, ticker, action)

    logger.info("[END] Daily trading task")
