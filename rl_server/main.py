# rl_server/main.py
from flask import Flask, request, jsonify
import threading

from model.train import train_model
from model.inference import get_recommendation
from scraper.sentiment_scraper import get_sentiment_score

app = Flask(__name__)

# 1) Trigger RL model training
@app.route('/train', methods=['POST'])
def train_endpoint():
    """
    Starts a background thread to train the RL model, so the HTTP request 
    doesn't block for a long time.
    """
    def run_training():
        train_model()

    thread = threading.Thread(target=run_training)
    thread.start()

    return jsonify({"message": "Training started in background."})

# 2) Get a recommendation (Buy/Hold/Sell) for one or more stocks
@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Expects JSON containing a list of stock tickers or current state data.
    Returns recommended actions from the trained model.
    """
    data = request.get_json()
    # data might look like: {"stocks": ["AAPL", "TSLA", "MSFT"]}
    recommendation = get_recommendation(data)
    return jsonify(recommendation)

# 3) Optional: Get sentiment score for a specific stock
@app.route('/sentiment', methods=['POST'])
def sentiment():
    """
    Expects JSON like: {"ticker": "AAPL"}
    Returns a sentiment score (mock or real) for the given ticker.
    """
    data = request.get_json()
    ticker = data.get("ticker", "")
    score = get_sentiment_score(ticker)
    return jsonify({"ticker": ticker, "sentiment_score": score})

if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, port=5001)
