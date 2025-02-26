# rl_server/model/inference.py

import os
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from model.train import MultiStockEnv  # Reuse the environment class

# Load the model once at import time (simple approach)
MODEL_PATH = "saved_models/ppo_multistock"
model = None
env = None

def _load_model():
    global model, env
    if model is None:
        if not os.path.exists(MODEL_PATH + ".zip"):
            print("Model file not found. Did you train it?")
            return
        # Create a dummy environment just for shape matching
        dummy_data = {"dates": [], "prices": {}, "tickers": ["AAPL"], "indicators": {}}
        dummy_data["prices"]["AAPL"] = np.array([0])  # minimal placeholder
        dummy_data["indicators"]["AAPL"] = {}
        indicators = []
        sentiment_scores = {}
        env_instance = MultiStockEnv(dummy_data, indicators, sentiment_scores)
        vec_env = DummyVecEnv([lambda: env_instance])

        # Load model
        loaded_model = PPO.load(MODEL_PATH, vec_env)
        model = loaded_model
        env = vec_env
        print("RL model loaded successfully.")

def get_recommendation(input_data):
    """
    input_data might be: {"stocks": ["AAPL", "MSFT", ...]}
    We'll generate an action from the loaded model. 
    In a real scenario, you'd gather the latest data for these stocks, 
    build an observation, then call model.predict().
    """
    _load_model()
    if model is None:
        return {"error": "Model not loaded. Please train first."}

    stocks = input_data.get("stocks", [])
    if not stocks:
        return {"error": "No stocks provided."}

    # In a real system, fetch current data for these stocks + indicators + sentiment
    # Then create an observation matching the environment's expected shape.

    # For demonstration, we assume each stock has random placeholders
    # shape = (len(stocks), #features)
    obs = np.random.rand(len(stocks), 7)  # e.g. price + 5 indicators + sentiment

    # stable-baselines requires a batch dimension
    obs = obs[np.newaxis, ...]

    action, _ = model.predict(obs, deterministic=True)
    # action might be an array of shape (num_stocks,) with values in {0,1,2}

    # Convert numeric action to textual recommendation
    action_map = {0: "SELL", 1: "HOLD", 2: "BUY"}
    results = []
    for i, stock in enumerate(stocks):
        results.append({
            "stock": stock,
            "action": action_map.get(action[0][i], "HOLD")  # default to HOLD if missing
        })

    return {"recommendations": results}
