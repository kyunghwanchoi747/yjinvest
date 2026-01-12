import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from src.stock_engine import StockProvider, resolve_ticker_with_ai
from src.notion_handler import NotionManager
from src.ai_analyst import generate_insight

# Load environment variables
load_dotenv()

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Stock Investment Diary", layout="wide")


def main():
    """
    Main function to run the Streamlit application.
    """
    st.title("📈 Stock Investment Diary")
    st.markdown("Fetch stock data, analyze with AI, and save to your Notion database.")

    # Initialize modules
    provider = StockProvider()

    # State management
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None
    if 'ai_insight' not in st.session_state:
        st.session_state.ai_insight = None
    if 'resolved_info' not in st.session_state:
        st.session_state.resolved_info = None  # (ticker, company_name, original_input)

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        with st.form(key='search_form'):
            ticker_input = st.text_input("티커 또는 회사명을 입력하세요 (예: 테슬라, AAPL)", value="테슬라")
            submit_button = st.form_submit_button(label='분석 시작 (Fetch & Analyze)')
        
        with st.expander("ℹ️ 티커 입력 도움말"):
            st.markdown("""
            - **AI가 자동으로 티커를 찾아줍니다!**
            - **한글 종목명**: 테슬라, 삼성전자, 엔비디아, 애플 등
            - **영문 티커**: `AAPL`, `TSLA`, `NVDA`
            - **한국 주식 티커**: `005930.KS` (코스피), `035720.KQ` (코스닥)
            """)
        
        st.divider()
        st.info("API 키 설정 상태를 확인하세요 (.env)")

    # Form Submission Logic
    if submit_button and ticker_input:
        with st.spinner('🔍 AI가 종목을 찾는 중...'):
            target_ticker, company_name = resolve_ticker_with_ai(ticker_input, GOOGLE_API_KEY)
            st.session_state.resolved_info = (target_ticker, company_name, ticker_input)

        if target_ticker != ticker_input.upper():
            st.toast(f"🔄 '{ticker_input}' → '{company_name} ({target_ticker})'로 변환되었습니다.")

        with st.spinner('데이터를 불러오는 중...'):
            data = provider.get_stock_data(target_ticker)
            
            if data:
                st.session_state.stock_data = data
                # Generate Insight
                try:
                    insight = generate_insight(data, GOOGLE_API_KEY)
                    if "Error" in insight and not GOOGLE_API_KEY:
                         st.session_state.ai_insight = "API 키가 설정되지 않아 분석을 수행할 수 없습니다."
                    else:
                        st.session_state.ai_insight = insight
                except Exception:
                    st.session_state.ai_insight = "AI 분석 중 일시적인 오류가 발생했습니다."
            else:
                st.error('데이터를 찾을 수 없습니다. 티커를 확인해주세요.')
                st.session_state.stock_data = None

    # Display Data
    if st.session_state.stock_data:
        data = st.session_state.stock_data
        info = data.get('info', {})

        # 1. Top Metrics Layout
        # Calculate change if previous close exists
        current_price = data['current_price']
        previous_close = info.get('previousClose', current_price)
        change_value = current_price - previous_close
        change_percent = (change_value / previous_close) * 100 if previous_close else 0
        volume = info.get('volume', 0)

        # 분석 중인 종목 표시 (AI 변환 정보 활용)
        resolved_info = st.session_state.resolved_info
        if resolved_info:
            ticker, company_name, original_input = resolved_info
            display_name = info.get('shortName', company_name)
            st.info(f"📊 **분석 중인 종목: {display_name} ({data['ticker']})**")

        st.subheader(f"{info.get('shortName', data['ticker'])} ({data['ticker']})")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(label="현재가", value=f"${current_price:,.2f}" if current_price < 10000 else f"₩{current_price:,.0f}", delta=f"{change_value:,.2f} ({change_percent:.2f}%)")
        with col_m2:
            st.metric(label="전일 종가", value=f"${previous_close:,.2f}" if previous_close < 10000 else f"₩{previous_close:,.0f}")
        with col_m3:
            st.metric(label="거래량", value=f"{volume:,}")

        st.divider()

        # 2. Main Layout: Chart (Left) + AI & News (Right)
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.write("### 🕯️ 1-Week Candlestick Chart")
            if not data['history'].empty:
                # Create Candlestick Chart
                fig = go.Figure(data=[go.Candlestick(
                    x=data['history'].index,
                    open=data['history']['Open'],
                    high=data['history']['High'],
                    low=data['history']['Low'],
                    close=data['history']['Close'],
                    increasing_line_color='red', # Korean style up
                    decreasing_line_color='blue' # Korean style down
                )])
                
                fig.update_layout(
                    xaxis_rangeslider_visible=False,
                    template="plotly_white",
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("차트 데이터를 불러올 수 없습니다.")

        with col_side:
            st.subheader("🤖 AI Insight")
            if st.session_state.ai_insight:
                insight = st.session_state.ai_insight
                # Check for various error conditions
                is_error = any(keyword in insight for keyword in ["Error", "API 키", "할당량", "차단", "유효하지"])
                if is_error:
                    st.warning(insight)
                elif insight.startswith("[MOCK"):
                    st.info("⚠️ API 키가 설정되지 않아 샘플 분석입니다.")
                    st.write(insight)
                else:
                    st.success(insight)
            else:
                st.write("분석 대기 중...")
            
            st.divider() 
            
            st.subheader("📰 Recent News")
            news_items = data.get('news', [])
            if news_items and len(news_items) > 0:
                for item in news_items[:5]:
                    if isinstance(item, dict):
                        title = item.get('title', item.get('headline', '제목 없음'))
                        link = item.get('link', item.get('url', '#'))
                        publisher = item.get('publisher', item.get('source', 'Unknown'))
                        # Ensure link is a string
                        if isinstance(link, dict):
                            link = link.get('url', '#')
                        if not link:
                            link = '#'
                        st.markdown(f"- [{title}]({link}) <span style='color:gray; font-size:0.8em'>- {publisher}</span>", unsafe_allow_html=True)
            else:
                st.info("관련 뉴스가 없습니다. (일부 종목은 뉴스를 제공하지 않습니다)")

        st.divider()

        # Save to Notion Section
        st.subheader("Notion 저장")
        with st.form("notion_save_form"):
             save_note = st.text_area("투자 메모 (선택사항)", placeholder="여기에 추가적인 메모를 남기세요...")
             save_btn = st.form_submit_button("💾 Notion에 기록하기")
             
             if save_btn:
                if not NOTION_TOKEN or not NOTION_DB_ID:
                    st.error("Notion API 설정이 누락되었습니다. .env 파일을 확인해주세요.")
                else:
                    try:
                        notion = NotionManager(NOTION_TOKEN, NOTION_DB_ID)
                        # Append user note to AI summary if exists
                        final_summary = st.session_state.ai_insight or ""
                        if save_note:
                            final_summary += f"\n\n[User Note]: {save_note}"

                        with st.spinner("Notion에 저장 중..."):
                            response = notion.add_stock_record(
                                ticker=data['ticker'],
                                price=data['current_price'],
                                summary=final_summary,
                                status="Analyzed"
                            )
                        
                        if response:
                            st.success(f"✅ {data['ticker']} 기록이 성공적으로 저장되었습니다!")
                        else:
                            st.error("❌ 저장에 실패했습니다. Notion 설정을 확인해주세요.")
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

if __name__ == "__main__":
    main()