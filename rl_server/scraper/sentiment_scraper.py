# rl_server/scraper/sentiment_scraper.py

import os
import time
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from alpha_vantage.news_sentiment import NewsSentiment
import random
from typing import Optional
from functools import lru_cache

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Get API key from environment variable
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
if not ALPHA_VANTAGE_API_KEY:
    print("Warning: ALPHA_VANTAGE_API_KEY not found in environment variables. Using mock data.")

@lru_cache(maxsize=100)
def get_sentiment_score(ticker: str) -> float:
    """
    Scrapes news for a given ticker and returns a sentiment score in [-1, 1].
    Uses Alpha Vantage API for news data and NLTK VADER for sentiment analysis.
    Falls back to random values if API key is not available.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        float: Sentiment score between -1 (very negative) and 1 (very positive)
    """
    if not ALPHA_VANTAGE_API_KEY:
        # Fallback to random values if no API key
        return random.uniform(-1, 1)
    
    try:
        # Initialize Alpha Vantage client
        news_sentiment = NewsSentiment(key=ALPHA_VANTAGE_API_KEY)
        
        # Get news feed for the ticker
        feed = news_sentiment.get_sentiment(ticker)
        
        if not feed or 'feed' not in feed:
            print(f"Warning: No news feed found for {ticker}")
            return 0.0
        
        # Analyze sentiment for each news item
        total_score = 0.0
        count = 0
        
        for item in feed['feed']:
            if 'title' in item:
                # Get sentiment score for the title
                sentiment = sia.polarity_scores(item['title'])
                total_score += sentiment['compound']  # compound score is already in [-1, 1]
                count += 1
        
        # Return average sentiment score, or 0 if no news items
        return total_score / count if count > 0 else 0.0
        
    except Exception as e:
        print(f"Error getting sentiment for {ticker}: {str(e)}")
        return 0.0
    finally:
        # Alpha Vantage has rate limits, so we need to wait
        time.sleep(12)  # Alpha Vantage free tier limit is 5 calls per minute

def get_sentiment_score(ticker: str) -> float:
    # Multiple sources
    alpha_score = get_alpha_vantage_sentiment(ticker)
    yahoo_score = get_yahoo_finance_sentiment(ticker)
    twitter_score = get_twitter_sentiment(ticker)
    
    # Weighted average
    return (0.4 * alpha_score + 0.3 * yahoo_score + 0.3 * twitter_score)

def analyze_article(item):
    title_sentiment = sia.polarity_scores(item['title'])
    content_sentiment = sia.polarity_scores(item['content'])
    return 0.3 * title_sentiment['compound'] + 0.7 * content_sentiment['compound']
