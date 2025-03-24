import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from model.train import MultiStockEnv, calculate_technical_indicators
from scraper.sentiment_scraper import get_sentiment_score
import requests
import time
import json

class TestTradingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.base_url = "http://localhost:5001"
        cls.test_tickers = ["AAPL", "MSFT", "GOOGL"]
        cls.start_date = datetime.now() - timedelta(days=365)
        cls.end_date = datetime.now()
        
        # Fetch test data
        cls.test_data = {}
        for ticker in cls.test_tickers:
            df = yf.download(ticker, start=cls.start_date, end=cls.end_date)
            cls.test_data[ticker] = df
    
    def test_technical_indicators(self):
        """Test technical indicator calculations."""
        for ticker, df in self.test_data.items():
            # Calculate indicators
            df_with_indicators = calculate_technical_indicators(df)
            
            # Check if all indicators are present
            required_indicators = [
                'SMA_20', 'SMA_50', 'EMA_20', 'RSI',
                'MACD', 'Signal_Line', 'BB_middle', 'BB_upper', 'BB_lower',
                'Volume_SMA', 'Volume_Ratio'
            ]
            
            for indicator in required_indicators:
                self.assertIn(indicator, df_with_indicators.columns)
                self.assertFalse(df_with_indicators[indicator].isnull().all())
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality."""
        for ticker in self.test_tickers:
            # Get sentiment score
            score = get_sentiment_score(ticker)
            
            # Check if score is within expected range
            self.assertGreaterEqual(score, -1.0)
            self.assertLessEqual(score, 1.0)
    
    def test_trading_environment(self):
        """Test the trading environment."""
        # Prepare test data
        data_dict = {
            "dates": self.test_data["AAPL"].index,
            "prices": {ticker: df["Close"] for ticker, df in self.test_data.items()},
            "tickers": self.test_tickers,
            "indicators": {
                ticker: calculate_technical_indicators(df)
                for ticker, df in self.test_data.items()
            }
        }
        
        # Create environment
        env = MultiStockEnv(
            data_dict,
            ["SMA_20", "RSI", "MACD"],
            {ticker: 0 for ticker in self.test_tickers}
        )
        
        # Test reset
        obs = env.reset()
        self.assertEqual(obs.shape, (len(self.test_tickers), 5))  # price + 3 indicators + portfolio
        
        # Test step
        action = np.array([1, 1, 1])  # Hold all positions
        obs, reward, done, info = env.step(action)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)
        self.assertIsInstance(info, dict)
    
    def test_api_endpoints(self):
        """Test API endpoints."""
        # Test model training
        response = requests.post(f"{self.base_url}/train")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        
        # Wait for training to complete
        time.sleep(5)
        
        # Test recommendations
        response = requests.post(
            f"{self.base_url}/recommend",
            json={"stocks": self.test_tickers}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations", response.json())
        
        # Test sentiment
        response = requests.post(
            f"{self.base_url}/sentiment",
            json={"ticker": "AAPL"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("sentiment_score", response.json())
        
        # Test portfolio
        response = requests.get(f"{self.base_url}/portfolio")
        self.assertEqual(response.status_code, 200)
        self.assertIn("balance", response.json())
        self.assertIn("positions", response.json())
    
    def test_trading_bot(self):
        """Test trading bot functionality."""
        # Start trading
        response = requests.post(f"{self.base_url}/start_trading")
        self.assertEqual(response.status_code, 200)
        
        # Wait for some trades to occur
        time.sleep(10)
        
        # Check portfolio status
        response = requests.get(f"{self.base_url}/portfolio")
        portfolio = response.json()
        
        # Verify portfolio structure
        self.assertIn("balance", portfolio)
        self.assertIn("positions", portfolio)
        self.assertIn("portfolio_value", portfolio)
        self.assertIn("trade_history", portfolio)
        
        # Stop trading
        response = requests.post(f"{self.base_url}/stop_trading")
        self.assertEqual(response.status_code, 200)
    
    def test_risk_management(self):
        """Test risk management features."""
        # Create environment with risk parameters
        data_dict = {
            "dates": self.test_data["AAPL"].index,
            "prices": {ticker: df["Close"] for ticker, df in self.test_data.items()},
            "tickers": self.test_tickers,
            "indicators": {
                ticker: calculate_technical_indicators(df)
                for ticker, df in self.test_data.items()
            }
        }
        
        env = MultiStockEnv(
            data_dict,
            ["SMA_20", "RSI", "MACD"],
            {ticker: 0 for ticker in self.test_tickers},
            initial_balance=100000,
            max_position_size=0.2
        )
        
        # Test position sizing
        action = np.array([2, 2, 2])  # Buy all stocks
        obs, reward, done, info = env.step(action)
        
        # Check position sizes
        for ticker in self.test_tickers:
            position_value = info["position_sizes"][ticker]
            self.assertLessEqual(position_value, 20000)  # 20% of 100000

if __name__ == '__main__':
    unittest.main(verbosity=2) 