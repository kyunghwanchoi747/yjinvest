from google import genai
from google.genai import types
from typing import Dict, Any

def generate_insight(stock_data: Dict[str, Any], api_key: str = None) -> str:
    """
    Generates an investment insight using Google Gemini based on stock data.
    If no API key is provided, returns a mock insight.

    Args:
        stock_data (Dict[str, Any]): Dictionary containing stock info, history, and news.
        api_key (str, optional): Google API key.

    Returns:
        str: A text summary/insight.
    """

    ticker = stock_data.get('ticker', 'Unknown')
    price = stock_data.get('current_price', 0.0)
    news = stock_data.get('news', [])

    # Extract headlines for context (handle different news structures)
    headlines = []
    for item in news[:5]:
        if isinstance(item, dict):
            title = item.get('title', item.get('headline', ''))
            if title:
                headlines.append(title)

    news_summary = "; ".join(headlines) if headlines else "No recent news available"

    if not api_key:
        return (f"[MOCK INSIGHT] The stock {ticker} is currently trading at ${price:,.2f}. "
                f"Recent news indicates: {news_summary}. "
                "Consider monitoring volatility.")

    try:
        # Initialize the new google-genai client
        client = genai.Client(api_key=api_key)

        prompt = (
            f"Analyze the following stock data for {ticker} as a professional financial analyst.\n"
            f"Current Price: {price}\n"
            f"Recent News Headlines: {news_summary}\n\n"
            "Provide a concise 3-sentence investment summary and sentiment analysis (Positive/Neutral/Negative). "
            "Focus on potential risks and opportunities based on the news provided. "
            "Respond in Korean."
        )

        # Use the new API with gemini-2.0-flash model
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        # Extract text from response
        if response and response.text:
            return response.text.strip()

        return "AI가 빈 응답을 반환했습니다. 다시 시도해주세요."

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
            return "Error: Google API 키가 유효하지 않습니다. .env 파일을 확인해주세요."
        elif "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
            return "Error: API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요."
        elif "PERMISSION" in error_msg.upper():
            return "Error: Gemini API 접근 권한이 없습니다. API 키 설정을 확인해주세요."
        elif "NOT_FOUND" in error_msg.upper() or "not found" in error_msg.lower():
            return "Error: 모델을 찾을 수 없습니다. API 설정을 확인해주세요."
        else:
            return f"Error generating AI insight: {error_msg}"
