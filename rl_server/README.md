# RL Server

This module serves as the RL server for the KaRLI_AI_invest project.  
It provides:
- **Training** endpoint (`POST /train`) to train an RL model using 10 years of stock data, 5 indicators, and optional sentiment.
- **Recommendation** endpoint (`POST /recommend`) to get Buy/Hold/Sell actions for given stocks.
- **Sentiment** endpoint (`POST /sentiment`) to scrape and return a naive sentiment score for a ticker.

## Setup

1. Clone the repository.
2. Navigate to `rl_server/`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
