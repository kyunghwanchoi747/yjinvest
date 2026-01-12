import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List

class StockProvider:
    """
    A class to fetch stock data using the yfinance library.
    """

    def __init__(self):
        """Initialize the StockProvider."""
        pass

    def _normalize_news(self, raw_news: Any) -> List[Dict[str, str]]:
        """
        Normalize news data from yfinance to a consistent format.
        Handles different yfinance versions and data structures.
        """
        normalized = []

        if not raw_news:
            return normalized

        try:
            for item in raw_news:
                if isinstance(item, dict):
                    # Handle different key names across yfinance versions
                    title = item.get('title', item.get('headline', '제목 없음'))
                    link = item.get('link', item.get('url', item.get('canonicalUrl', {}).get('url', '#')))
                    publisher = item.get('publisher', item.get('source', 'Unknown'))

                    # Handle nested structure in some versions
                    if isinstance(link, dict):
                        link = link.get('url', '#')

                    normalized.append({
                        'title': title,
                        'link': link if link else '#',
                        'publisher': publisher
                    })
        except Exception:
            pass

        return normalized

    def get_stock_data(self, ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetches real-time price, history, and news for a given ticker.

        Args:
            ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL').

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing stock data, or None if an error occurs.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)

            # Fetch 1-week history
            history = ticker.history(period="1wk")
            if history.empty:
                raise ValueError(f"No data found for ticker '{ticker_symbol}'.")

            # Get current price (use 'regularMarketPrice' or the last close if unavailable)
            # info dictionary keys can vary, fast_info is more reliable for current price
            try:
                current_price = ticker.fast_info.last_price
            except Exception:
                # Fallback to last close price from history
                current_price = history['Close'].iloc[-1] if not history.empty else 0.0

            # Get recent news with error handling
            try:
                raw_news = ticker.news
                news = self._normalize_news(raw_news)
            except Exception:
                news = []

            # Get info with error handling
            try:
                info = ticker.info
            except Exception:
                info = {}

            return {
                "ticker": ticker_symbol.upper(),
                "current_price": current_price,
                "history": history,
                "news": news,
                "info": info
            }

        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            return None
