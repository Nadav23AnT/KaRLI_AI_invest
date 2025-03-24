# KaRLI AI Investment System

A sophisticated AI-powered trading system that combines Reinforcement Learning, sentiment analysis, and technical indicators for automated stock trading.

## Features

### 1. Reinforcement Learning Model
- Uses PPO (Proximal Policy Optimization) algorithm
- Trained on 10 years of historical data
- Considers multiple technical indicators and sentiment
- Supports multiple stocks simultaneously
- Position sizing strategies:
  - Equal weight
  - Kelly Criterion
  - Risk-based sizing

### 2. Technical Analysis
- Price-based indicators:
  - SMA (20, 50 days)
  - EMA (20 days)
  - RSI (14 days)
  - MACD with Signal Line
  - Bollinger Bands
- Volume indicators:
  - Volume SMA
  - Volume Ratio

### 3. Sentiment Analysis
- Multiple data sources:
  - Alpha Vantage News API
  - Yahoo Finance
  - Twitter (planned)
- NLTK VADER sentiment analyzer
- Cached results for efficiency
- Fallback to mock data when API unavailable

### 4. Risk Management
- Position sizing limits (max 20% per stock)
- Stop loss (2%)
- Take profit (5%)
- Transaction cost consideration (0.1%)
- Market hours checking
- Portfolio value tracking

### 5. Trading Bot
- Real-time market data via yfinance
- Automated trading during market hours
- Portfolio tracking and management
- Trade history logging
- Performance monitoring

## API Endpoints

### 1. Model Training
```bash
POST /train
```
Starts background training of the RL model.

### 2. Trading Control
```bash
POST /start_trading
POST /stop_trading
```
Controls the trading bot.

### 3. Portfolio Management
```bash
GET /portfolio
```
Returns current portfolio status, positions, and recent trades.

### 4. Analysis
```bash
POST /recommend
POST /sentiment
```
Get trading recommendations and sentiment scores.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/KaRLI_AI_invest.git
cd KaRLI_AI_invest/rl_server
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export ALPHA_VANTAGE_API_KEY=your_api_key_here
```

4. Train the model:
```bash
curl -X POST http://localhost:5001/train
```

5. Start the trading bot:
```bash
curl -X POST http://localhost:5001/start_trading
```

## Usage Examples

### Get Trading Recommendations
```bash
curl -X POST http://localhost:5001/recommend \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "MSFT", "GOOGL"]}'
```

### Check Portfolio Status
```bash
curl http://localhost:5001/portfolio
```

### Get Sentiment Score
```bash
curl -X POST http://localhost:5001/sentiment \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

## Architecture

### Components
1. **RL Model** (`model/train.py`)
   - Environment implementation
   - Model training logic
   - Technical indicators calculation

2. **Inference** (`model/inference.py`)
   - Model loading and prediction
   - Real-time data processing
   - Recommendation generation

3. **Sentiment Analysis** (`scraper/sentiment_scraper.py`)
   - News data collection
   - Sentiment scoring
   - Caching mechanism

4. **Trading Bot** (`main.py`)
   - Portfolio management
   - Trade execution
   - Risk management
   - API endpoints

## Logging

All trading activities are logged to `trading_bot.log` with the following information:
- Trade executions
- Portfolio updates
- Error messages
- Market status
- Performance metrics

## Risk Warning

This is an experimental trading system. Use at your own risk. The system:
- May incur losses
- Requires careful monitoring
- Should be tested thoroughly before real trading
- Is not financial advice

## Future Improvements

1. Additional data sources
2. More sophisticated position sizing
3. Advanced risk management
4. Backtesting capabilities
5. Performance analytics
6. Web interface
7. Mobile notifications
