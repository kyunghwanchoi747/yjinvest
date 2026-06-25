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

import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from src.stock_engine import StockProvider, resolve_ticker_with_ai
from src.notion_handler import NotionManager
from src.ai_analyst import generate_insight
from src.financial_data import FinanceDataReader

# Load environment variables
load_dotenv()

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="YJ INVEST - AI Private Investment Diary", layout="wide")


def check_password() -> bool:
    """
    Returns True if the user had the correct password.
    """
    app_password = os.getenv("APP_PASSWORD", "")
    if not app_password:
        # 비밀번호가 비어있으면 로그인 절차 생략
        return True

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

    # CSS를 이용해 깔끔한 로그인 폼 구성
    st.markdown("""
        <style>
        .login-box {
            max-width: 450px;
            margin: 80px auto;
            padding: 40px;
            border-radius: 15px;
            background-color: #ffffff;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            text-align: center;
        }
        .login-title {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 10px;
        }
        .login-desc {
            color: #64748b;
            font-size: 0.9em;
            margin-bottom: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<h2 class="login-title">🔐 YJ INVEST Private Access</h2>', unsafe_allow_html=True)
        st.markdown('<p class="login-desc">허가받은 파트너만 접속 가능한 개인 투자 분석 공간입니다.</p>', unsafe_allow_html=True)
        
        password_input = st.text_input("액세스 비밀번호 입력", type="password", key="login_pwd_input")
        login_btn = st.button("인증 및 입장하기", use_container_width=True)
        
        if login_btn:
            if password_input == app_password:
                st.session_state["authenticated"] = True
                st.success("인증에 성공했습니다! 페이지를 불러옵니다...")
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다. 다시 입력해 주세요.")
        st.markdown('</div>', unsafe_allow_html=True)

    return False


def main():
    """
    Main function to run the Streamlit application.
    """
    # 비밀번호 확인 검사
    if not check_password():
        return

    st.title("📈 YJ INVEST - AI Private Investment Diary")
    st.markdown("거시경제 통계와 주식 데이터를 연동하여, AI와 함께 투자 전략을 수립하고 Notion에 기록하는 나만의 프라이빗 비서입니다.")

    # Initialize modules
    provider = StockProvider()
    finance_reader = FinanceDataReader()

    # Fetch Macro Economic Data (ECOS + Mock fallback)
    macro_data = finance_reader.get_macro_summary()

    # State management
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None
    if 'ai_insight' not in st.session_state:
        st.session_state.ai_insight = None
    if 'resolved_info' not in st.session_state:
        st.session_state.resolved_info = None  # (ticker, company_name, original_input)

    # Sidebar for Analysis Control
    with st.sidebar:
        st.header("🔍 종목 분석")
        
        with st.form(key='search_form'):
            ticker_input = st.text_input("티커 또는 회사명을 입력하세요 (예: 테슬라, AAPL)", value="테슬라")
            submit_button = st.form_submit_button(label='분석 시작 (Fetch & Analyze)', use_container_width=True)
        
        with st.expander("ℹ️ 티커 입력 도움말"):
            st.markdown("""
            - **AI가 자동으로 티커를 찾아줍니다!**
            - **한글 종목명**: 테슬라, 삼성전자, 엔비디아 등
            - **영문 티커**: `AAPL`, `TSLA`, `NVDA`
            - **한국 주식 티커**: `005930.KS` (코스피), `035720.KQ` (코스닥)
            """)
        
        st.divider()
        st.write("🔑 **보안 연결 상태**")
        st.info("프라이빗 모드 활성화됨")
        if st.button("로그아웃"):
            st.session_state["authenticated"] = False
            st.rerun()

    # Main Layout Tabs
    tab1, tab2 = st.tabs(["📊 주식 투자 분석", "🌐 거시경제 지표 (ECOS)"])

    # --- TAB 1: Stock Analysis ---
    with tab1:
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
                    # Generate Insight (Pass macro_data to prompt engineering)
                    try:
                        insight = generate_insight(data, macro_data, GOOGLE_API_KEY)
                        if "Error" in insight and not GOOGLE_API_KEY:
                             st.session_state.ai_insight = "API 키가 설정되지 않아 분석을 수행할 수 없습니다."
                        else:
                            st.session_state.ai_insight = insight
                    except Exception as e:
                        st.session_state.ai_insight = f"AI 분석 중 일시적인 오류가 발생했습니다: {e}"
                else:
                    st.error('데이터를 찾을 수 없습니다. 티커를 확인해주세요.')
                    st.session_state.stock_data = None

        # Display Stock Data
        if st.session_state.stock_data:
            data = st.session_state.stock_data
            info = data.get('info', {})

            current_price = data['current_price']
            previous_close = info.get('previousClose', current_price)
            change_value = current_price - previous_close
            change_percent = (change_value / previous_close) * 100 if previous_close else 0
            volume = info.get('volume', 0)

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

            col_main, col_side = st.columns([2, 1])
            
            with col_main:
                st.write("### 🕯️ 주가 1주일 차트")
                if not data['history'].empty:
                    fig = go.Figure(data=[go.Candlestick(
                        x=data['history'].index,
                        open=data['history']['Open'],
                        high=data['history']['High'],
                        low=data['history']['Low'],
                        close=data['history']['Close'],
                        increasing_line_color='red',
                        decreasing_line_color='blue'
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
                st.subheader("🤖 AI 거시경제 + 주식 종합 분석 보고서")
                if st.session_state.ai_insight:
                    insight = st.session_state.ai_insight
                    is_error = any(keyword in insight for keyword in ["Error", "API 키", "할당량", "차단", "유효하지"])
                    if is_error:
                        st.warning(insight)
                    elif insight.startswith("**[MOCK"):
                        st.info("⚠️ API 키가 설정되지 않아 예시 분석 결과가 표시됩니다.")
                        st.write(insight)
                    else:
                        st.success(insight)
                else:
                    st.write("왼쪽에서 분석 시작 버튼을 눌러주세요.")
                
                st.divider() 
                
                st.subheader("📰 관련 최근 뉴스")
                news_items = data.get('news', [])
                if news_items and len(news_items) > 0:
                    for item in news_items[:5]:
                        if isinstance(item, dict):
                            title = item.get('title', item.get('headline', '제목 없음'))
                            link = item.get('link', item.get('url', '#'))
                            publisher = item.get('publisher', item.get('source', 'Unknown'))
                            if isinstance(link, dict):
                                link = link.get('url', '#')
                            if not link:
                                link = '#'
                            st.markdown(f"- [{title}]({link}) <span style='color:gray; font-size:0.8em'>- {publisher}</span>", unsafe_allow_html=True)
                else:
                    st.info("관련 뉴스가 없습니다.")

            st.divider()

            # Save to Notion Section
            st.subheader("📝 Notion에 분석 결과 기록")
            with st.form("notion_save_form"):
                 save_note = st.text_area("투자자 개인 메모 (선택사항)", placeholder="나의 생각이나 추가적인 분석 의견을 남기세요...")
                 save_btn = st.form_submit_button("💾 Notion 데이터베이스에 저장", use_container_width=True)
                 
                 if save_btn:
                    if not NOTION_TOKEN or not NOTION_DB_ID:
                        st.error("Notion API 설정이 누락되었습니다. .env 파일을 확인해주세요.")
                    else:
                        try:
                            notion = NotionManager(NOTION_TOKEN, NOTION_DB_ID)
                            final_summary = st.session_state.ai_insight or ""
                            if save_note:
                                final_summary += f"\n\n[투자자 노트]: {save_note}"

                            with st.spinner("Notion 전송 중..."):
                                response = notion.add_stock_record(
                                    ticker=data['ticker'],
                                    price=data['current_price'],
                                    summary=final_summary,
                                    status="Analyzed"
                                )
                            
                            if response:
                                st.success(f"✅ Notion 데이터베이스에 {data['ticker']} 분석 및 투자 전략이 저장되었습니다!")
                            else:
                                st.error("❌ 저장에 실패했습니다. Notion 토큰 및 DB ID를 점검해주세요.")
                        except Exception as e:
                            st.error(f"오류 발생: {e}")

    # --- TAB 2: Macro Economics ---
    with tab2:
        st.subheader("🌐 거시경제 지표 및 시장 요약")
        st.write("한국은행 경제통계시스템(ECOS) API 및 주요 시장 금리 지표 현황입니다.")
        
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.metric(label="한국 기준금리", value=f"{macro_data['korea_base_rate']}%", delta="BOK 기준")
        with col_c2:
            st.metric(label="미국 기준금리", value=f"{macro_data['us_base_rate']}%", delta="FRB 기준")
        with col_c3:
            st.metric(label="원/달러 환율", value=f"{macro_data['exchange_rate']:,} 원")
        with col_c4:
            st.metric(label="소비자물가상승률 (CPI)", value=f"{macro_data['cpi_inflation']}%")

        st.info(f"데이터 출처: {macro_data['korea_base_rate_source']}")

        # Plotly Line Chart for BOK Base Rate
        st.write("### 📈 한국은행 기준금리 추이")
        rate_history = macro_data.get("korea_base_rate_history", {})
        if rate_history and "dates" in rate_history:
            df_rate = pd.DataFrame({
                "Date": rate_history["dates"],
                "Rate (%)": rate_history["rates"]
            })
            fig_rate = go.Figure()
            fig_rate.add_trace(go.Scatter(
                x=df_rate["Date"],
                y=df_rate["Rate (%)"],
                mode='lines+markers',
                name='기준금리',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8)
            ))
            fig_rate.update_layout(
                xaxis_title="연월",
                yaxis_title="금리 (%)",
                template="plotly_white",
                height=400,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_rate, use_container_width=True)
        else:
            st.write("금리 추이 차트 데이터를 불러올 수 없습니다.")


if __name__ == "__main__":
    main()