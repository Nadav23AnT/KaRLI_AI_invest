# rl_server/model/inference.py

import os
import numpy as np
import yfinance as yf
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from functools import lru_cache
from datetime import datetime, timedelta

from model.train import MultiStockEnv, calculate_technical_indicators
from scraper.sentiment_scraper import get_sentiment_score

# Load the model once at import time (simple approach)
MODEL_PATH = "saved_models/ppo_multistock"
model = None
env = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _load_model():
    global model, env
    if model is None:
        if not os.path.exists(MODEL_PATH + ".zip"):
            logger.error("Model file not found. Did you train it?")
            return
        
        # Create a dummy environment just for shape matching
        dummy_data = {"dates": [], "prices": {}, "tickers": ["AAPL"], "indicators": {}}
        dummy_data["prices"]["AAPL"] = np.array([0])
        dummy_data["indicators"]["AAPL"] = {}
        indicators = ["SMA_20", "SMA_50", "RSI", "MACD", "Signal_Line", 
                     "BB_upper", "BB_lower", "Volume_Ratio"]
        sentiment_scores = {}
        env_instance = MultiStockEnv(dummy_data, indicators, sentiment_scores)
        vec_env = DummyVecEnv([lambda: env_instance])

        # Load model
        loaded_model = PPO.load(MODEL_PATH, vec_env)
        model = loaded_model
        env = vec_env
        logger.info("RL model loaded successfully.")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
@lru_cache(maxsize=100)
def _get_current_data(ticker: str) -> pd.DataFrame:
    """Fetch current market data for a ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=100)  # Get enough data for indicators
    
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if len(df) == 0:
        raise ValueError(f"No data found for {ticker}")
    
    df = calculate_technical_indicators(df)
    return df

def get_recommendation(input_data: dict) -> dict:
    """
    Get trading recommendations for a list of stocks.
    
    Args:
        input_data: Dictionary containing list of stocks to analyze
                   {"stocks": ["AAPL", "MSFT", ...]}
    
    Returns:
        Dictionary containing recommendations and additional info
    """
    _load_model()
    if model is None:
        return {"error": "Model not loaded. Please train first."}

    stocks = input_data.get("stocks", [])
    if not stocks:
        return {"error": "No stocks provided."}

    try:
        # Fetch current data for all stocks
        current_data = {}
        indicators = ["SMA_20", "SMA_50", "RSI", "MACD", "Signal_Line", 
                     "BB_upper", "BB_lower", "Volume_Ratio"]
        
        for ticker in stocks:
            df = _get_current_data(ticker)
            current_data[ticker] = df
        
        # Get sentiment scores
        sentiment_scores = {}
        for ticker in stocks:
            sentiment_scores[ticker] = get_sentiment_score(ticker)
        
        # Create observation array
        obs = []
        for ticker in stocks:
            df = current_data[ticker]
            current_price = df["Close"].iloc[-1]
            
            # Normalize price (using last 100 days of data)
            price_mean = df["Close"].mean()
            price_std = df["Close"].std()
            normalized_price = (current_price - price_mean) / price_std
            
            row = [normalized_price]
            
            # Add technical indicators
            for ind in indicators:
                value = df[ind].iloc[-1]
                row.append(value)
            
            # Add sentiment
            row.append(sentiment_scores[ticker])
            
            # Add position size (0 for inference)
            row.append(0)
            
            # Add portfolio value (1 for inference)
            row.append(1)
            
            obs.append(row)
        
        # Add batch dimension for stable-baselines
        obs = np.array(obs, dtype=np.float32)[np.newaxis, ...]
        
        # Get model prediction
        action, _ = model.predict(obs, deterministic=True)
        
        # Convert actions to recommendations
        action_map = {0: "SELL", 1: "HOLD", 2: "BUY"}
        results = []
        for i, stock in enumerate(stocks):
            current_price = current_data[stock]["Close"].iloc[-1]
            results.append({
                "stock": stock,
                "action": action_map.get(action[0][i], "HOLD"),
                "current_price": current_price,
                "sentiment_score": sentiment_scores[stock]
            })
        
        return {
            "recommendations": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return {"error": f"Failed to get recommendations: {str(e)}"}
