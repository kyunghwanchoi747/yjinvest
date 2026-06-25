from google import genai
from google.genai import types
from typing import Dict, Any

def generate_insight(stock_data: Dict[str, Any], macro_data: Dict[str, Any] = None, api_key: str = None) -> str:
    """
    Google Gemini AI를 사용하여 주식 데이터와 거시경제 데이터를 결합한 투자 분석 및 전략을 생성합니다.
    API 키가 없으면 시연용 분석 보고서를 반환합니다.

    Args:
        stock_data (Dict[str, Any]): 주식 정보, 주가 역사, 뉴스 등이 담긴 딕셔너리.
        macro_data (Dict[str, Any], optional): ECOS 등을 통해 수집한 거시경제 지표.
        api_key (str, optional): Google API Key.

    Returns:
        str: 한국어로 작성된 거시경제 및 주식 종합 투자 전략 분석 보고서.
    """

    ticker = stock_data.get('ticker', 'Unknown')
    price = stock_data.get('current_price', 0.0)
    news = stock_data.get('news', [])

    # 뉴스 헤드라인 요약 추출
    headlines = []
    for item in news[:5]:
        if isinstance(item, dict):
            title = item.get('title', item.get('headline', ''))
            if title:
                headlines.append(title)

    news_summary = "; ".join(headlines) if headlines else "최근 뉴스가 제공되지 않습니다."

    # 거시경제 기본값 설정
    macro_info = macro_data or {
        "korea_base_rate": 3.50,
        "us_base_rate": 5.25,
        "cpi_inflation": 2.7,
        "exchange_rate": 1380.0
    }

    if not api_key:
        return (
            f"**[MOCK ANALYSIS - API 키 미등록 샘플]**\n\n"
            f"### 1. 거시경제 및 시장 요약\n"
            f"- 한국 기준금리: {macro_info['korea_base_rate']}% | 미국 기준금리: {macro_info['us_base_rate']}%\n"
            f"- 환율: {macro_info['exchange_rate']}원 | 물가상승률(CPI): {macro_info['cpi_inflation']}%\n\n"
            f"### 2. {ticker} 종목 현황 및 리스크\n"
            f"- 현재가: ${price:,.2f} / ₩{price:,.0f} 수준에서 거래 중입니다.\n"
            f"- 최근 관련 뉴스: {news_summary[:150]}...\n\n"
            f"### 3. 추천 투자 전략\n"
            f"- 금리 상황과 최근 흐름을 고려할 때 분할 매수로 접근하는 것을 권장합니다. 리스크 관리를 위해 비중을 조절하세요."
        )

    try:
        # Google GenAI 클라이언트 초기화
        client = genai.Client(api_key=api_key)

        prompt = (
            f"당신은 금융투자 전문가이자 1인 투자법인 최고투자책임자(CIO)입니다.\n"
            f"다음 주식 정보 및 거시경제 상황을 연계분석하여 최적의 투자 전략 보고서를 한국어로 작성해주세요.\n\n"
            f"--- [분석 대상 주식 정보] ---\n"
            f"- 티커 심볼: {ticker}\n"
            f"- 현재 가격: {price}\n"
            f"- 최근 뉴스 요약: {news_summary}\n\n"
            f"--- [거시경제 현황 지표] ---\n"
            f"- 한국 기준금리: {macro_info.get('korea_base_rate')}% (출처: {macro_info.get('korea_base_rate_source', 'BOK')})\n"
            f"- 미국 기준금리: {macro_info.get('us_base_rate')}%\n"
            f"- 물가상승률 (CPI): {macro_info.get('cpi_inflation')}%\n"
            f"- 원/달러 환율: {macro_info.get('exchange_rate')}원\n\n"
            f"--- [요청 양식] ---\n"
            f"다음 3가지 영역을 상세하게 채워서 읽기 쉽도록 마크다운(Markdown) 형식으로 응답해 주세요.\n"
            f"1. **거시경제 여건 분석**: 현재 금리 수준과 환율이 해당 종목/업종에 미치는 긍정적/부정적 요인 설명\n"
            f"2. **종목 리스크 스크리닝**: 뉴스 헤드라인과 가격 정보를 근거로 한 핵심 리스크 분석\n"
            f"3. **종합 투자 및 매매 전략**: 매수/매도/관망 여부와 함께 구체적인 비중 조절안, 백테스팅 관점의 팁 제안"
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

        return "AI가 빈 분석 보고서를 반환했습니다. 다시 시도해 주세요."

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
            return "Error: Google API 키가 유효하지 않습니다. .env 파일을 확인해주세요."
        elif "QUOTA" in error_msg.upper() or "LIMIT" in error_msg.upper():
            return "Error: API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요."
        elif "PERMISSION" in error_msg.upper():
            return "Error: Gemini API 접근 권한이 없습니다. API 키 설정을 확인해주세요."
        else:
            return f"Error generating AI insight: {error_msg}"

