import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from google import genai

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


def resolve_ticker_with_ai(user_input: str, api_key: str = None) -> Tuple[str, str]:
    """
    Gemini API를 사용하여 회사명을 주식 티커로 변환합니다.

    Args:
        user_input (str): 사용자가 입력한 회사명 또는 티커 (예: 테슬라, 삼성전자, AAPL)
        api_key (str): Google API 키

    Returns:
        Tuple[str, str]: (티커, 회사명) 튜플
            - 티커: yfinance에서 사용할 수 있는 티커 심볼
            - 회사명: 해당 회사의 이름
    """
    cleaned_input = user_input.strip()

    # API 키가 없으면 입력값을 그대로 반환
    if not api_key:
        return (cleaned_input.upper(), cleaned_input)

    # 이미 티커 형식인지 확인 (영문 대문자 + 숫자 조합, 한국 주식 포함)
    if cleaned_input.upper().replace(".", "").replace("-", "").isalnum() and cleaned_input.isascii():
        # 티커 형식이면 회사명만 조회
        return (cleaned_input.upper(), cleaned_input.upper())

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""당신은 주식 티커 전문가입니다. 사용자가 입력한 회사명을 주식 티커로 변환해주세요.

입력: {cleaned_input}

규칙:
1. 미국 주식: 티커만 반환 (예: TSLA, AAPL, NVDA)
2. 한국 주식: 6자리 숫자 + .KS(코스피) 또는 .KQ(코스닥) 형식으로 반환
   - 삼성전자 → 005930.KS
   - SK하이닉스 → 000660.KS
   - 카카오 → 035720.KS
3. 회사를 찾을 수 없으면 "UNKNOWN"을 반환

반드시 다음 형식으로만 응답하세요 (다른 설명 없이):
티커|회사명

예시:
- 입력: 테슬라 → TSLA|Tesla
- 입력: 삼성전자 → 005930.KS|삼성전자
- 입력: 애플 → AAPL|Apple
- 입력: 엔비디아 → NVDA|NVIDIA"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if response and response.text:
            result = response.text.strip()
            # "티커|회사명" 형식 파싱
            if "|" in result:
                parts = result.split("|", 1)
                ticker = parts[0].strip()
                company_name = parts[1].strip() if len(parts) > 1 else cleaned_input
                return (ticker, company_name)
            else:
                # 파이프가 없으면 전체를 티커로 간주
                return (result.strip(), cleaned_input)

        return (cleaned_input.upper(), cleaned_input)

    except Exception as e:
        print(f"Error resolving ticker with AI: {e}")
        return (cleaned_input.upper(), cleaned_input)
