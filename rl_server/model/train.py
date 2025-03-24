# rl_server/model/train.py

import os
import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gym
from typing import Dict, List, Tuple

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for a stock."""
    # Price-based indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_20'] = df['Close'].ewm(span=20).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    
    return df

class MultiStockEnv(gym.Env):
    """
    Custom environment for multiple stocks trading.
    Each step, the agent must decide: 0=Sell, 1=Hold, 2=Buy for each stock.
    """
    def __init__(self, data: Dict, indicators: List[str], sentiment: Dict[str, float], 
                 initial_balance: float = 100000, transaction_cost: float = 0.001,
                 position_sizing: str = "equal_weight", max_position_size: float = 0.2):
        super(MultiStockEnv, self).__init__()
        self.data = data
        self.indicators = indicators
        self.sentiment = sentiment
        self.transaction_cost = transaction_cost
        self.position_sizing = position_sizing  # "equal_weight", "kelly", "risk_based"
        self.max_position_size = max_position_size  # Maximum position size as fraction of portfolio
        
        self.current_step = 0
        self.num_stocks = len(data["tickers"])
        self.action_space = gym.spaces.MultiDiscrete([3]*self.num_stocks)
        
        # Observation space: [price, indicators, sentiment, position_size, portfolio_value]
        obs_len = 1 + len(indicators) + 1 + 1 + 1
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.num_stocks, obs_len), dtype=np.float32
        )
        
        # Portfolio tracking
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {ticker: 0 for ticker in data["tickers"]}
        self.portfolio_value = initial_balance
        
        # Position sizing parameters
        self.win_rates = {ticker: 0.5 for ticker in data["tickers"]}  # For Kelly criterion
        self.volatilities = self._calculate_volatilities()
        
        # Normalization parameters
        self.price_mean = {}
        self.price_std = {}
        self._calculate_normalization_params()
    
    def _calculate_volatilities(self) -> Dict[str, float]:
        """Calculate historical volatility for each stock."""
        volatilities = {}
        for ticker in self.data["tickers"]:
            prices = self.data["prices"][ticker]
            returns = prices.pct_change().dropna()
            volatilities[ticker] = returns.std() * np.sqrt(252)  # Annualized volatility
        return volatilities
    
    def _calculate_position_size(self, ticker: str, action: int) -> int:
        """
        Calculate position size based on selected strategy.
        
        Args:
            ticker: Stock ticker
            action: Action taken (0=Sell, 1=Hold, 2=Buy)
            
        Returns:
            Number of shares to trade
        """
        if action == 0:  # Sell
            return self.positions[ticker]  # Sell entire position
        elif action == 1:  # Hold
            return 0
        
        # For Buy actions, calculate position size based on strategy
        current_price = self.data["prices"][ticker].iloc[self.current_step]
        
        if self.position_sizing == "equal_weight":
            # Equal weight across all stocks
            target_value = self.portfolio_value / self.num_stocks
            shares = int(target_value / current_price)
            
        elif self.position_sizing == "kelly":
            # Kelly Criterion: f = (p * b - q) / b
            # where p = win rate, q = loss rate, b = win/loss ratio
            win_rate = self.win_rates[ticker]
            kelly_fraction = win_rate - (1 - win_rate)
            target_value = self.portfolio_value * kelly_fraction
            shares = int(target_value / current_price)
            
        elif self.position_sizing == "risk_based":
            # Risk-based sizing using volatility
            vol = self.volatilities[ticker]
            risk_factor = 1 / vol  # Higher volatility = smaller position
            target_value = self.portfolio_value * risk_factor * self.max_position_size
            shares = int(target_value / current_price)
        
        else:
            # Default to equal weight
            target_value = self.portfolio_value / self.num_stocks
            shares = int(target_value / current_price)
        
        # Apply maximum position size constraint
        max_shares = int(self.portfolio_value * self.max_position_size / current_price)
        return min(shares, max_shares)
    
    def _calculate_normalization_params(self):
        """Calculate normalization parameters for each stock."""
        for ticker in self.data["tickers"]:
            prices = self.data["prices"][ticker]
            self.price_mean[ticker] = prices.mean()
            self.price_std[ticker] = prices.std()
    
    def _normalize_price(self, ticker: str, price: float) -> float:
        """Normalize price using pre-calculated parameters."""
        return (price - self.price_mean[ticker]) / self.price_std[ticker]
    
    def reset(self):
        """Reset the environment to initial state."""
        self.current_step = 0
        self.balance = self.initial_balance
        self.positions = {ticker: 0 for ticker in self.data["tickers"]}
        self.portfolio_value = self.initial_balance
        return self._get_observation()
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Execute trading actions and return new state.
        
        Args:
            action: Array of actions (0=Sell, 1=Hold, 2=Buy) for each stock
            
        Returns:
            observation: New state observation
            reward: Reward for the action
            done: Whether episode is finished
            info: Additional information
        """
        old_portfolio_value = self.portfolio_value
        
        # Execute trades
        for i, ticker in enumerate(self.data["tickers"]):
            current_price = self.data["prices"][ticker].iloc[self.current_step]
            action_taken = action[i]
            
            # Calculate position size based on strategy
            shares = self._calculate_position_size(ticker, action_taken)
            
            if action_taken == 0:  # Sell
                if shares > 0:
                    cost = shares * current_price * self.transaction_cost
                    self.balance += shares * current_price - cost
                    self.positions[ticker] -= shares
            elif action_taken == 2:  # Buy
                if shares > 0 and self.balance > 0:
                    cost = shares * current_price * self.transaction_cost
                    total_cost = shares * current_price + cost
                    if total_cost <= self.balance:
                        self.balance -= total_cost
                        self.positions[ticker] += shares
        
        # Update portfolio value
        self.portfolio_value = self.balance
        for ticker in self.data["tickers"]:
            current_price = self.data["prices"][ticker].iloc[self.current_step]
            self.portfolio_value += self.positions[ticker] * current_price
        
        # Calculate reward (Sharpe ratio-like)
        returns = (self.portfolio_value - old_portfolio_value) / old_portfolio_value
        reward = returns * 100  # Scale up for better learning
        
        # Update step
        self.current_step += 1
        done = self.current_step >= len(self.data["dates"]) - 1
        
        # Get new observation
        obs = self._get_observation()
        info = {
            "portfolio_value": self.portfolio_value,
            "balance": self.balance,
            "positions": self.positions,
            "position_sizes": {ticker: self.positions[ticker] * self.data["prices"][ticker].iloc[self.current_step] 
                             for ticker in self.data["tickers"]}
        }
        
        return obs, reward, done, info
    
    def _get_observation(self) -> np.ndarray:
        """Build observation array for all stocks."""
        obs = []
        for ticker in self.data["tickers"]:
            current_price = self.data["prices"][ticker].iloc[self.current_step]
            normalized_price = self._normalize_price(ticker, current_price)
            
            row = [normalized_price]
            
            # Add technical indicators
            for ind in self.indicators:
                value = self.data["indicators"][ticker][ind].iloc[self.current_step]
                row.append(value)
            
            # Add sentiment
            row.append(self.sentiment.get(ticker, 0))
            
            # Add position size (normalized)
            position_value = self.positions[ticker] * current_price
            normalized_position = position_value / self.initial_balance
            row.append(normalized_position)
            
            # Add portfolio value (normalized)
            normalized_portfolio = self.portfolio_value / self.initial_balance
            row.append(normalized_portfolio)
            
            obs.append(row)
        
        return np.array(obs, dtype=np.float32)

def train_model():
    print("Starting RL training...")
    
    # 1) Select tickers
    tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA",
               "NVDA", "JNJ", "XOM", "JPM", "V", "PG", "HD", "BAC", "DIS",
               "MA", "PFE", "CVX", "KO", "PEP", "ABBV", "COST", "MRK", "ABT", 
               "T", "WMT", "ADBE", "NFLX", "CRM", "ORCL", "PYPL"]
    
    # 2) Fetch historical data
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=3650)
    
    data_dict = {"dates": None, "prices": {}, "tickers": tickers, "indicators": {}}
    
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if len(df) == 0:
            print(f"Warning: no data for {ticker}, skipping.")
            continue
        
        df = df.dropna()
        if data_dict["dates"] is None:
            data_dict["dates"] = df.index
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Store data
        data_dict["prices"][ticker] = df["Close"]
        data_dict["indicators"][ticker] = df
    
    # 3) Define indicators to use
    indicators = ["SMA_20", "SMA_50", "RSI", "MACD", "Signal_Line", 
                 "BB_upper", "BB_lower", "Volume_Ratio"]
    
    # 4) Get sentiment scores (placeholder for now)
    sentiment_scores = {ticker: 0 for ticker in tickers}
    
    # 5) Create environment with position sizing
    env = MultiStockEnv(
        data_dict, 
        indicators, 
        sentiment_scores,
        position_sizing="risk_based",  # Try different strategies: "equal_weight", "kelly", "risk_based"
        max_position_size=0.2  # Maximum 20% of portfolio in one stock
    )
    
    # 6) Wrap environment
    vec_env = DummyVecEnv([lambda: env])
    
    # 7) Train model with adjusted hyperparameters for position sizing
    model = PPO(
        "MlpPolicy",
        vec_env,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        verbose=1
    )
    
    # Train for more steps for better performance
    model.learn(total_timesteps=100000)
    
    # 8) Save model
    os.makedirs("saved_models", exist_ok=True)
    model.save("saved_models/ppo_multistock")
    
    print("Training completed. Model saved to saved_models/ppo_multistock")
