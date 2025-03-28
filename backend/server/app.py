from flask import Flask, request, jsonify
from flask_cors import CORS

import mongo_utils
from Enums.risk import RISK
from alpacaTrading import create_client, get_account_info, get_open_positions, get_open_orders, get_portfolio_history, get_recent_activities

app = Flask(__name__)
CORS(app)

RISK_LEVELS = [risk.value for risk in RISK]

# Simulated user data (Replace with database)
USER_DATA = {
    "itai": {"balance": 10500.75, "overallProfit": 12.3, "availableCash": 2500.00, "tradingStatus": "Active"},
    "jane_smith": {"balance": 8900.50, "overallProfit": 9.8, "availableCash": 1800.00, "tradingStatus": "Active"}
}

# Temporary storage for Alpaca keys (replace with a DB in real app)
USER_ALPACA_CREDS = {
    "itai": {
        "api_key": "PKI4K2CEOZ4WG89MFWMM",
        "api_secret": "eaWthufyMFbTktSPDtc1zE6ZBH1dDQwGJTS3NhVZ",
        "base_url": "https://paper-api.alpaca.markets"
    },
    "jane_smith": {
        "api_key": "PKI4K2CEOZ4WG89MFWMM",
        "api_secret": "eaWthufyMFbTktSPDtc1zE6ZBH1dDQwGJTS3NhVZ",
        "base_url": "https://paper-api.alpaca.markets"
    }
}


@app.route('/signUp', methods=['POST'])
def sign_up():
    data = request.json
    user_name = data.get('username')
    password = data.get('password')
    age = data.get('age')
    risk_level = data.get('risk')

    if not user_name or not password or not age or risk_level not in RISK_LEVELS:
        return jsonify({"error": "Invalid input: Some fields are missing"}), 400

    if mongo_utils.sign_up(user_name, password, age, risk_level):
        return jsonify(True), 200
    return jsonify({"error": "Username already exists"}), 400


@app.route('/signIn', methods=['POST'])
def sign_in():
    data = request.json
    user_name = data.get('username')
    password = data.get('password')

    if mongo_utils.sing_in(user_name, password):
        return jsonify(True)
    return "username or password are incorrect", 401


@app.route('/summary', methods=['POST'])
def get_summary():
    """
    Fetch user-specific trading summary, including full Alpaca account data.
    """
    data = request.json
    username = data.get("username")

    if not username or username not in USER_ALPACA_CREDS:
        return jsonify({"error": "User not found"}), 404

    # Fetch Alpaca credentials and create the client
    alpaca_creds = USER_ALPACA_CREDS[username]
    client = create_client(alpaca_creds["api_key"], alpaca_creds["api_secret"], alpaca_creds["base_url"])

    # Fetch account and positions using Alpaca client
    account_info = get_account_info(client)
    portfolio_history = get_portfolio_history(client)
    recent_activities = get_recent_activities(client)

    # Get the most recent portfolio history values
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
