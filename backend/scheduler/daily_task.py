import logging
from Enums.rl_variables import tickers
from RL_model.load_model import predict_stocks_actions
from alpacaTrading import create_client
from alpacaTrading.account import submit_order, get_client_position, get_open_positions, get_account_info
from mongo_utils import get_all_users_with_credentials
from scheduler.yahooFinance import set_daily_finance_data

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Send Orders to Alpaca ---
def send_order_to_alpaca(api_key, api_secret, symbol, action):
    client = create_client(api_key, api_secret)

    try:
        if action == "BUY":  # Buy
            # submit_order(client, symbol, 1, "buy", "market", "day") #TODO decide how to sumbit buy orders using risk-level and other buy actions
            logger.info("[ORDER] Buy %s", symbol)

        elif action == "SELL":  # Sell
            try:
                position = get_client_position(client, symbol)

                if position:
                    # submit_order(client, symbol, position.qty, "sell", "market", "day") #TODO check function
                    logger.info("[ORDER] Sell %s", symbol)
            except Exception as e:
                logger.info("[SKIP] No position to sell for %s", symbol)
        elif action == "HOLD":  # Hold
            logger.info("[HOLD] %s", symbol)
    except Exception as e:
        logger.error("[ERROR] Order failed for %s: %s", symbol, e)


# --- Main Scheduled Logic ---
def daily_task():
    logger.info("[START] Daily trading task")
    set_daily_finance_data(tickers)
    print("Done fetching")

    stocks_actions = predict_stocks_actions(tickers)
    print(f"Done getting data {stocks_actions}")

    if not stocks_actions:
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

        logger.info("KEY: %s , SECRET: %s", api_key, api_secret)
        logger.info("[USER] %s - Risk: %s", username, risk)
        for ticker, action in stocks_actions:
            logger.info("[ACTION] %s: %s", ticker, action)
            send_order_to_alpaca(api_key, api_secret, ticker, action)

    logger.info("[END] Daily trading task")
