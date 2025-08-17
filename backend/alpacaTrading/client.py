# alpaca_account_utils/client.py

from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient

def create_client(api_key, api_secret):
    return TradingClient(api_key, api_secret, paper=True, raw_data=True)

def create_stock_historical_data_client(api_key, api_secret):
    return StockHistoricalDataClient(api_key=api_key, secret_key=api_secret)

