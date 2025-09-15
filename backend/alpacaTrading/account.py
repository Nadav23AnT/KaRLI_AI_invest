# alpaca_account_utils/account.py

from alpaca.trading.client import TradingClient 
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.enums import QueryOrderStatus, OrderSide, OrderType, TimeInForce
from alpaca.trading.requests import GetOrdersRequest, GetPortfolioHistoryRequest, OrderRequest

from alpaca_trade_api.rest import APIError

def get_account_info(client: TradingClient):
    try:
        return client.get_account()
    except APIError as e:
        return {"error": str(e)}

def get_open_positions(client: TradingClient):
    try:
        return client.get_all_positions()
    except APIError as e:
        return {"error": str(e)}

def get_open_orders(client: TradingClient):
    try:
        return client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.CLOSED))
    except APIError as e:
        return {"error": str(e)}

def get_portfolio_history(client: TradingClient, days=30):
    try:
        return client.get_portfolio_history(history_filter=GetPortfolioHistoryRequest(period=f"{days}D"))
    except APIError as e:
        return {"error": str(e)}

def get_recent_activities(client: TradingClient, activity_type=None): #TODO use "FILL" to show the client only completed buy/sell transactions
    try:
        # They have not defined a function for getting activities in the new trading python SDK
        return client.get(
            "/account/activities" + (("?activity_types=" + activity_type) if activity_type else "")
        )
    except APIError as e:
        return {"error": str(e)}

def submit_order(
        client: TradingClient,
        symbol: str,
        quantity: float,
        action: OrderSide,
        type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY):
    try:
        order = client.submit_order(order_data=OrderRequest(
            symbol=symbol,
            qty=quantity,
            side=action,
            type=type,
            time_in_force=time_in_force
        ))
        return order
    except APIError as e:
        return {"error": str(e)}

def get_client_position(client: TradingClient, symbol):
    try:
        return client.get_open_position(symbol)
    except APIError as e:
        return {"error": str(e)}

def get_stock_latest_trade_price(client: StockHistoricalDataClient, symbol) -> float:
    try:
        response = client.get_stock_latest_trade(request_params=StockLatestTradeRequest(symbol_or_symbols=symbol))
        return response.get(symbol).price
    except APIError as e:
        return {"error": str(e)}
