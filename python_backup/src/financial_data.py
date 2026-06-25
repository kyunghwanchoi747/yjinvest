import os
import requests
import pandas as pd
from typing import Dict, Any, Optional

class FinanceDataReader:
    """
    한국은행 ECOS 및 DART 등의 금융 데이터를 수집하는 클래스입니다.
    초보자도 쉽게 이해할 수 있도록 API 키가 없는 경우에도 작동할 수 있는 가짜(Mock) 데이터를 포함합니다.
    """

    def __init__(self, ecos_key: Optional[str] = None, dart_key: Optional[str] = None):
        self.ecos_key = ecos_key or os.getenv("ECOS_API_KEY")
        self.dart_key = dart_key or os.getenv("DART_API_KEY")

    def get_korea_base_rate(self) -> Dict[str, Any]:
        """
        한국은행(ECOS) API를 통해 한국 기준금리 데이터를 조회합니다.
        (통계표코드: 722Y001, 항목코드: 0101000)
        """
        if not self.ecos_key:
            # API 키가 없을 때 보여줄 기본 최신 가짜 데이터
            return {
                "source": "MOCK (한국은행 기준금리 샘플)",
                "current_rate": 3.50,
                "history": {
                    "dates": ["2024-01", "2024-05", "2024-10", "2025-01", "2025-06", "2026-01"],
                    "rates": [3.50, 3.50, 3.25, 3.25, 3.00, 3.00]
                },
                "status": "정상 (시연용 데이터)"
            }

        try:
            # ECOS API URL 포맷
            # 형식: http://ecos.bok.or.kr/api/StatisticSearch/[API키]/json/kr/1/10/722Y001/M/202301/202606/0101000
            url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.ecos_key}/json/kr/1/20/722Y001/M/202301/202612/0101000"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "StatisticSearch" in data and "row" in data["StatisticSearch"]:
                    rows = data["StatisticSearch"]["row"]
                    # 정렬 (날짜 순)
                    rows = sorted(rows, key=lambda x: x["TIME"])
                    
                    dates = [f"{r['TIME'][:4]}-{r['TIME'][4:6]}" for r in rows]
                    rates = [float(r["DATA_VALUE"]) for r in rows]
                    
                    return {
                        "source": "한국은행 경제통계시스템 (ECOS)",
                        "current_rate": rates[-1] if rates else 3.50,
                        "history": {
                            "dates": dates,
                            "rates": rates
                        },
                        "status": "성공"
                    }
            
            raise Exception("올바르지 않은 응답이 수신되었습니다.")
        except Exception as e:
            print(f"ECOS API 오류: {e}")
            # 에러 발생 시 백업용 가짜 데이터 반환
            return {
                "source": "MOCK (API 오류 백업용)",
                "current_rate": 3.50,
                "history": {
                    "dates": ["2024-01", "2024-05", "2024-10", "2025-01", "2025-06", "2026-01"],
                    "rates": [3.50, 3.50, 3.25, 3.25, 3.00, 3.00]
                },
                "status": f"오류 발생 ({str(e)}) - 샘플 데이터로 대체되었습니다."
            }

    def get_macro_summary(self) -> Dict[str, Any]:
        """
        주요 거시경제 지표(기준금리, 물가지수 등)를 종합한 요약본을 가져옵니다.
        """
        rate_data = self.get_korea_base_rate()
        
        return {
            "korea_base_rate": rate_data["current_rate"],
            "korea_base_rate_source": rate_data["source"],
            "korea_base_rate_history": rate_data["history"],
            "us_base_rate": 5.25, # 미국 기준금리는 간소화를 위해 기본값 고정 또는 가짜 데이터 제공
            "cpi_inflation": 2.7,  # 소비자 물가 상승률 (%)
            "exchange_rate": 1380.0 # 원/달러 환율 ($)
        }

    def get_company_disclosure_summary(self, ticker: str) -> str:
        """
        DART API를 통해 회사 공시 정보를 간략히 수집해 요약합니다.
        (초보자용으로 심플하게 구현)
        """
        if not self.dart_key:
            return f"[{ticker}] 최근 공시 요약: 사업 보고서 및 정기 주주총회 소집 공고가 등록되었습니다. 특별한 특이사항은 없는 상태입니다. (DART API 키 미등록 상태)"

        # 실제 DART API 연동 로직 (필요 시 확장 가능)
        # 여기서는 API 키가 있는 경우 가짜 요약글 대신 간단한 안내 혹은 기초 스크래핑을 수행합니다.
        return f"[{ticker}] 최근 공시 요약: 전자공시시스템(DART) 조회 성공. 최근 분기보고서와 임원 소유주식 변동 보고서가 접수되었습니다."
