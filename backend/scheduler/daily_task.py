import logging
from collections import defaultdict
from time import sleep

from Enums.rl_variables import tickers
from RL_model.model_inference import predict_stocks_actions
from alpacaTrading import create_client
from alpacaTrading.account import submit_order, get_open_positions, get_account_info, get_stock_latest_trade_price
from mongo_utils import get_all_users_with_credentials
from scheduler.yahooFinance import set_daily_finance_data

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
OVERFLOW_BUY_BUFFER = 1


def handle_model_recommendation(api_key, api_secret, action_map):
    client = create_client(api_key, api_secret)

    # Get all current positions once
    current_positions = {pos["symbol"]: pos for pos in get_open_positions(client)}

    # --- SELL ---
    for symbol in action_map.get("SELL", []):
        position = current_positions.get(symbol)
        if position:
            try:
                # submit_order(
                #     client,
                #     symbol=symbol,
                #     quantity=position["qty"],
                #     action="sell",
                #     type="market",
                #     time_in_force="day"
                # )
                print(f"[SELL] Submitted sell order for {symbol}, qty={position["qty"]}")
            except Exception as e:
                print(f"[ERROR] Failed to sell {symbol}: {e}")
        else:
            print(f"[INFO] No position to sell for {symbol}")

    # Wait for sales to settle
    sleep(2)

    # --- HOLD ---
    for symbol in action_map.get("HOLD", []):
        if symbol in current_positions:
            print(f"[HOLD] Already holding {symbol}")
        else:
            print(f"[HOLD] Not holding {symbol}, fitted to HOLD")

    # --- BUY ---
    buy_tickers = action_map.get("BUY", [])
    if not buy_tickers:
        return

    try:
        account = get_account_info(client)
        left_positions = get_open_positions(client)
        if not left_positions:
            cash = 2 * float(account["cash"]) / 3 # if all the money is available so set only 2/3 of the money to invest
        else:
            cash = float(account["cash"])
        cash_per_stock = cash / len(buy_tickers)
    except Exception as e:
        print(f"[ERROR] Failed to retrieve account cash: {e}")
        return

    for symbol in buy_tickers:
        try:
            price = get_stock_latest_trade_price(client, symbol)
            qty = int(cash_per_stock // price - OVERFLOW_BUY_BUFFER)

            if qty <= 0:
                print(f"[BUY] Not enough funds to buy {symbol}")
                continue

            # submit_order(
            #     client,
            #     symbol=symbol,
            #     quantity=qty,
            #     action="buy",
            #     type="market",
            #     time_in_force="day"
            # )
            print(f"[BUY] Submitted buy order for {symbol}, qty= {qty}, price= {price:.2f}, cash_per_stock= {cash_per_stock}")
        except Exception as e:
            print(f"[ERROR] Failed to buy {symbol}: {e}")

# --- Main Scheduled Logic ---
def daily_task():
    logger.info("[START] Daily trading task")
    set_daily_finance_data(tickers)
    logger.info("Inserted new daily finance data to MongoDB")

    stocks_actions = predict_stocks_actions(tickers)
    action_map = defaultdict(list)

    if not stocks_actions:
        logger.warning("No actions received.")
        return

    for ticker, action in stocks_actions:
        action_map[action].append(ticker)
    action_map = dict(action_map)

    print(f"Done getting data {action_map}")

    users = get_all_users_with_credentials()
    for user in users:
        username = user["username"]
        risk = user["risk"]
        api_key = user["api_key"]
        api_secret = user["api_secret"]

        if not api_key or not api_secret:
            logger.warning("[SKIP] Missing Alpaca credentials for %s", username)
            continue

        logger.info("KEY: %s , SECRET: %s", api_key, api_secret)
        logger.info("USER: %s , Risk: %s", username, risk)
        handle_model_recommendation(api_key, api_secret, action_map)

    logger.info("[END] Daily trading task")
