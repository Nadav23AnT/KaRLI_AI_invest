# rl_server/model/train.py

import os
import datetime
import yfinance as yf
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gym
import numpy as np

# Example custom environment
class MultiStockEnv(gym.Env):
    """
    Simplified custom environment for multiple stocks.
    Each step, the agent must decide: 0=Sell, 1=Hold, 2=Buy for each stock.
    In practice, you'd use a MultiDiscrete action space or another approach 
    to handle multiple stocks at once.
    """
    def __init__(self, data, indicators, sentiment, initial_balance=100000):
        super(MultiStockEnv, self).__init__()
        self.data = data
        self.indicators = indicators
        self.sentiment = sentiment

        # Example: single-step example (not truly realistic)
        self.current_step = 0
        self.num_stocks = len(data["tickers"])
        self.action_space = gym.spaces.MultiDiscrete([3]*self.num_stocks)  
        # 3 possible actions (Sell=0, Hold=1, Buy=2) per stock

        # Observation might be [price, 5 indicators, sentiment], repeated for each stock
        obs_len = 1 + len(indicators) + 1  # e.g., price + 5 indicators + 1 sentiment
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.num_stocks, obs_len), dtype=np.float32
        )

        self.initial_balance = initial_balance
        self.balance = initial_balance

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        return self._get_observation()

    def step(self, action):
        """
        Execute the action:
        - 0=Sell, 1=Hold, 2=Buy for each stock
        This is a naive placeholder.
        """
        # For demonstration, let's do no real transaction logic. 
        # Typically you'd adjust holdings, track PnL, etc.
        reward = 0.0
        self.current_step += 1
        done = self.current_step >= len(self.data["dates"])  # e.g., end of data
        obs = self._get_observation()
        info = {}
        return obs, reward, done, info

    def _get_observation(self):
        """
        Build an observation array for all stocks at the current step.
        [ [price, indicator1, ..., indicator5, sentiment], ... ] 
        """
        obs = []
        for i, ticker in enumerate(self.data["tickers"]):
            price = self.data["prices"][ticker].iloc[self.current_step]
            row = [price]
            for ind in self.indicators:
                row.append(self.data["indicators"][ticker][ind].iloc[self.current_step])
            row.append(self.sentiment.get(ticker, 0))  # sentiment score
            obs.append(row)
        return np.array(obs, dtype=np.float32)


def train_model():
    print("Starting RL training...")

    # 1) Select your 30 tickers
    tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA",
               "NVDA", "JNJ", "XOM", "JPM", "V", "PG", "HD", "BAC", "DIS",
               "MA", "PFE", "CVX", "KO", "PEP", "ABBV", "COST", "MRK", "ABT", 
               "T", "WMT", "ADBE", "NFLX", "CRM", "ORCL", "PYPL"]  # example 30

    # 2) Fetch 10 years of historical data
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=3650)  # ~10 years

    data_dict = {"dates": None, "prices": {}, "tickers": tickers, "indicators": {}}

    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) == 0:
            print(f"Warning: no data for {ticker}, skipping.")
            continue

        df = df.dropna()
        if data_dict["dates"] is None:
            data_dict["dates"] = df.index

        # Store adjusted close as "price"
        data_dict["prices"][ticker] = df["Adj Close"]

    # 3) Compute 5 indicators (placeholder)
    # For demonstration, let's define them as columns in a sub-dict
    data_dict["indicators"] = {}
    indicators = ["SMA", "EMA", "RSI", "MACD", "VOL"]  # Example 5
    for ticker in tickers:
        if ticker not in data_dict["prices"]:
            continue
        df = pd.DataFrame(data_dict["prices"][ticker]).rename(columns={"Adj Close": "Price"})
        df["SMA"] = df["Price"].rolling(window=20).mean()
        df["EMA"] = df["Price"].ewm(span=20).mean()
        # RSI, MACD, VOL etc. can be computed similarly or with a library
        df["RSI"] = 50  # placeholder
        df["MACD"] = 0  # placeholder
        df["VOL"] = df["Price"].rolling(window=10).std()

        data_dict["indicators"][ticker] = df

    # 4) Get sentiment scores for each ticker (placeholder)
    # Real logic might come from a web scraper or stored data
    sentiment_scores = {ticker: 0 for ticker in tickers}  # dummy 0 for now

    # 5) Create the environment
    env = MultiStockEnv(data_dict, indicators, sentiment_scores)

    # 6) Wrap the env in a DummyVecEnv for stable-baselines
    vec_env = DummyVecEnv([lambda: env])

    # 7) Train using PPO (as an example)
    model = PPO("MlpPolicy", vec_env, verbose=1)
    model.learn(total_timesteps=10000)

    # 8) Save the model
    os.makedirs("saved_models", exist_ok=True)
    model.save("saved_models/ppo_multistock")

    print("Training completed. Model saved to saved_models/ppo_multistock")
