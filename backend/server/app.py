from flask import Flask, request, jsonify
from flask_cors import CORS

import mongo_utils
from Enums.risk import RISK
from alpacaTrading import create_client, get_account_info, get_open_positions, get_open_orders, get_portfolio_history, get_recent_activities

app = Flask(__name__)
CORS(app) 

RISK_LEVELS = [risk.value for risk in RISK]
base_url = "https://paper-api.alpaca.markets"


@app.route('/signUp', methods=['POST'])
def sign_up():
    data = request.json
    user_name = data.get('username')
    password = data.get('password')
    age = data.get('age')
    risk_level = data.get('risk')
    broker_api_key = data.get('brokerApiKey')
    broker_api_secret = data.get('brokerApiSecret')

    if not user_name or not password or not age or risk_level not in RISK_LEVELS:
        return jsonify({"error": "Invalid input: Some fields are missing"}), 400

    client = create_client(broker_api_key, broker_api_secret, base_url)
    account_info = get_account_info(client)

    if account_info.get("error") is not None:
        return jsonify({"error": "User don't have brokerAPI account"}), 400

    if mongo_utils.sign_up(user_name, password, age, risk_level, broker_api_key, broker_api_secret):
        return jsonify(True), 200
    return jsonify({"error": "Username already exists"}), 400


@app.route('/signIn', methods=['POST'])
def sign_in():
    data = request.json
    user_name = data.get('username')
    password = data.get('password')

    if mongo_utils.sign_in(user_name, password):
        return jsonify(True)
    return "username or password are incorrect", 401


@app.route('/summary', methods=['POST'])
def get_summary():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "User not found"}), 404

    broker_api_credentials = mongo_utils.get_user_brokerApi_credentials(username)

    if broker_api_credentials is None:
        return jsonify({"error": "Sorry, broker API credentials not found for this user."}), 404

    client = create_client(broker_api_credentials["api_key"], broker_api_credentials["api_secret"], base_url)

    account_info = get_account_info(client)
    portfolio_history = get_portfolio_history(client)
    recent_activities = get_recent_activities(client)
    latest_equity = portfolio_history["equity"][-1]
    latest_profit_loss = portfolio_history["profit_loss"][-1]
    latest_profit_loss_pct = portfolio_history["profit_loss_pct"][-1]
    latest_timestamp = portfolio_history["timestamp"][-1]

    # Prepare the response object
    response = {
        "accountInfo": {
            "account_blocked": account_info["account_blocked"],
            "balance_asof": account_info["balance_asof"],
            "cash": account_info["cash"],
            "created_at": account_info["created_at"],
            "currency": account_info["currency"],
            "equity": account_info["equity"],
            "status": account_info["status"],
            "trading_blocked": account_info["trading_blocked"]
        },
        "portfolioHistory": {
            "latest_equity": latest_equity,
            "latest_profit_loss": latest_profit_loss,
            "latest_profit_loss_pct": latest_profit_loss_pct,
            "latest_timestamp": latest_timestamp
        },
        "recentActivities": [
            {"activity_type": activity["activity_type"], "date": activity["date"], "net_amount": activity["net_amount"], "status": activity["status"]}
            for activity in recent_activities
        ]
    }

    return jsonify(response), 200

@app.route('/stop-trading', methods=['POST'])
def stop_trading():
    """
    Stop trading for a specific user.
    """
    data = request.json
    username = data.get("username")

    # Simulated user data (Replace with database)
    USER_DATA = {
        "itai": {"balance": 10500.75, "overallProfit": 12.3, "availableCash": 2500.00, "tradingStatus": "Active"},
        "jane_smith": {"balance": 8900.50, "overallProfit": 9.8, "availableCash": 1800.00, "tradingStatus": "Active"}
    }

    if not username or username not in USER_DATA:
        return jsonify({"error": "User not found"}), 404

    USER_DATA[username]["tradingStatus"] = "Stopped"
    return jsonify({"message": "Trading has been stopped!", "tradingStatus": "Stopped"}), 200


@app.route("/risks", methods=["GET"])
def get_risk_levels():
    return jsonify({"risks": RISK_LEVELS})


if __name__ == '__main__':
    print("app is running!")
    app.run(debug=True, threaded=False)
