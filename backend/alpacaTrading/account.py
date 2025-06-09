# alpaca_account_utils/account.py

from alpaca_trade_api.rest import APIError

def get_account_info(client):
    try:
        account = client.get_account()
        return account._raw
    except APIError as e:
        return {"error": str(e)}

def get_open_positions(client):
    try:
        positions = client.list_positions()
        return [p._raw for p in positions]
    except APIError as e:
        return {"error": str(e)}

def get_open_orders(client):
    try:
        orders = client.list_orders(status='open')
        return [o._raw for o in orders]
    except APIError as e:
        return {"error": str(e)}

def get_portfolio_history(client, days=30):
    try:
        history = client.get_portfolio_history(period=f"{days}D")
        return history._raw
    except APIError as e:
        return {"error": str(e)}

def get_recent_activities(client, activity_type=None): #TODO use "FILL" to show the client only completed buy/sell transactions
    try:
        activities = client.get_activities(activity_type) if activity_type else client.get_activities()
        return [a._raw for a in activities]
    except APIError as e:
        return {"error": str(e)}


def submit_order(client, symbol, quantity , action, type="market", time_in_force="day"):
    try:
        order  = client.submit_order(symbol=symbol, qty=quantity, side=action, type=type, time_in_force=time_in_force)
        return order
    except APIError as e:
        return {"error": str(e)}


def get_client_position(client, symbol):
    try:
        position = client.get_position(symbol)
        return position
    except APIError as e:
        return {"error": str(e)}
