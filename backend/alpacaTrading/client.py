# alpaca_account_utils/client.py

from alpaca_trade_api.rest import REST

def create_client(api_key, api_secret, base_url="https://paper-api.alpaca.markets"):
    return REST(api_key, api_secret, base_url)
