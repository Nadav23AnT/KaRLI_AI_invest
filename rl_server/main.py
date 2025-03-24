# rl_server/main.py
from flask import Flask, request, jsonify
import threading
import time
import logging
from datetime import datetime, time as dt_time
import pytz
from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd

from model.train import train_model
from model.inference import get_recommendation
from scraper.sentiment_scraper import get_sentiment_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, initial_balance: float = 100000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions: Dict[str, int] = {}  # Current positions
        self.trade_history: List[Dict] = []  # Track all trades
        self.is_trading = False
        self.trading_thread = None
        self.last_update = None
        
        # Trading parameters
        self.max_position_size = 0.2  # Maximum 20% of portfolio in one stock
        self.stop_loss = 0.02  # 2% stop loss
        self.take_profit = 0.05  # 5% take profit
        self.transaction_cost = 0.001  # 0.1% transaction cost
        
        # Market hours (EST)
        self.market_open = dt_time(9, 30)
        self.market_close = dt_time(16, 0)
        
        logger.info(f"TradingBot initialized with ${initial_balance:,.2f} initial balance")
    
    def is_market_open(self) -> bool:
        """Check if the market is currently open."""
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est).time()
        return self.market_open <= current_time <= self.market_close
    
    def get_portfolio_value(self) -> float:
        """Calculate current portfolio value including positions."""
        total_value = self.balance
        
        for ticker, shares in self.positions.items():
            try:
                current_price = yf.Ticker(ticker).info.get('regularMarketPrice')
                if current_price:
                    total_value += shares * current_price
            except Exception as e:
                logger.error(f"Error getting price for {ticker}: {str(e)}")
        
        return total_value
    
    def execute_trade(self, ticker: str, action: str, shares: int) -> bool:
        """Execute a trade with proper error handling and logging."""
        try:
            current_price = yf.Ticker(ticker).info.get('regularMarketPrice')
            if not current_price:
                logger.error(f"Could not get price for {ticker}")
                return False
            
            cost = shares * current_price * (1 + self.transaction_cost)
            
            if action == "BUY":
                if cost > self.balance:
                    logger.warning(f"Insufficient funds for {ticker} purchase")
                    return False
                self.balance -= cost
                self.positions[ticker] = self.positions.get(ticker, 0) + shares
                
            elif action == "SELL":
                if shares > self.positions.get(ticker, 0):
                    logger.warning(f"Insufficient shares for {ticker} sale")
                    return False
                self.balance += cost
                self.positions[ticker] -= shares
            
            # Record trade
            self.trade_history.append({
                "timestamp": datetime.now().isoformat(),
                "ticker": ticker,
                "action": action,
                "shares": shares,
                "price": current_price,
                "cost": cost,
                "portfolio_value": self.get_portfolio_value()
            })
            
            logger.info(f"Executed {action} {shares} shares of {ticker} at ${current_price:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade for {ticker}: {str(e)}")
            return False
    
    def check_stop_loss_take_profit(self):
        """Check and execute stop loss and take profit orders."""
        for ticker, shares in list(self.positions.items()):
            if shares == 0:
                continue
                
            try:
                current_price = yf.Ticker(ticker).info.get('regularMarketPrice')
                if not current_price:
                    continue
                
                # Get average entry price from trade history
                entry_trades = [t for t in self.trade_history 
                              if t["ticker"] == ticker and t["action"] == "BUY"]
                if not entry_trades:
                    continue
                
                avg_entry_price = sum(t["price"] * t["shares"] for t in entry_trades) / sum(t["shares"] for t in entry_trades)
                current_return = (current_price - avg_entry_price) / avg_entry_price
                
                # Check stop loss
                if current_return <= -self.stop_loss:
                    logger.info(f"Stop loss triggered for {ticker}")
                    self.execute_trade(ticker, "SELL", shares)
                
                # Check take profit
                elif current_return >= self.take_profit:
                    logger.info(f"Take profit triggered for {ticker}")
                    self.execute_trade(ticker, "SELL", shares)
                    
            except Exception as e:
                logger.error(f"Error checking stop loss/take profit for {ticker}: {str(e)}")
    
    def trading_loop(self):
        """Main trading loop that runs during market hours."""
        while self.is_trading:
            try:
                if not self.is_market_open():
                    logger.info("Market is closed. Waiting...")
                    time.sleep(60)
                    continue
                
                # Get current positions
                current_positions = list(self.positions.keys())
                
                # Get recommendations for current positions and watchlist
                watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Example watchlist
                all_tickers = list(set(current_positions + watchlist))
                
                recommendations = get_recommendation({"stocks": all_tickers})
                
                if "error" in recommendations:
                    logger.error(f"Error getting recommendations: {recommendations['error']}")
                    time.sleep(60)
                    continue
                
                # Process recommendations
                for rec in recommendations["recommendations"]:
                    ticker = rec["stock"]
                    action = rec["action"]
                    current_price = rec["current_price"]
                    
                    # Calculate position size based on portfolio value
                    portfolio_value = self.get_portfolio_value()
                    max_position_value = portfolio_value * self.max_position_size
                    shares = int(max_position_value / current_price)
                    
                    if action == "BUY" and ticker not in self.positions:
                        self.execute_trade(ticker, "BUY", shares)
                    elif action == "SELL" and ticker in self.positions:
                        self.execute_trade(ticker, "SELL", self.positions[ticker])
                
                # Check stop loss and take profit
                self.check_stop_loss_take_profit()
                
                # Update last update time
                self.last_update = datetime.now()
                
                # Wait before next iteration
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                time.sleep(60)
    
    def start_trading(self):
        """Start the trading bot."""
        if self.is_trading:
            logger.warning("Trading bot is already running")
            return
        
        self.is_trading = True
        self.trading_thread = threading.Thread(target=self.trading_loop)
        self.trading_thread.start()
        logger.info("Trading bot started")
    
    def stop_trading(self):
        """Stop the trading bot."""
        self.is_trading = False
        if self.trading_thread:
            self.trading_thread.join()
        logger.info("Trading bot stopped")

# Initialize Flask app and trading bot
app = Flask(__name__)
trading_bot = TradingBot()

@app.route('/train', methods=['POST'])
def train_endpoint():
    """Start model training in background."""
    def run_training():
        train_model()
    
    thread = threading.Thread(target=run_training)
    thread.start()
    return jsonify({"message": "Training started in background."})

@app.route('/start_trading', methods=['POST'])
def start_trading_endpoint():
    """Start the trading bot."""
    trading_bot.start_trading()
    return jsonify({"message": "Trading bot started"})

@app.route('/stop_trading', methods=['POST'])
def stop_trading_endpoint():
    """Stop the trading bot."""
    trading_bot.stop_trading()
    return jsonify({"message": "Trading bot stopped"})

@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio status."""
    return jsonify({
        "balance": trading_bot.balance,
        "positions": trading_bot.positions,
        "portfolio_value": trading_bot.get_portfolio_value(),
        "trade_history": trading_bot.trade_history[-10:]  # Last 10 trades
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    """Get trading recommendations."""
    data = request.get_json()
    recommendation = get_recommendation(data)
    return jsonify(recommendation)

@app.route('/sentiment', methods=['POST'])
def sentiment():
    """Get sentiment score for a ticker."""
    data = request.get_json()
    ticker = data.get("ticker", "")
    score = get_sentiment_score(ticker)
    return jsonify({"ticker": ticker, "sentiment_score": score})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
