# YJ INVEST 배포 가이드

## 1. 환경 변수 설정

`.env.local` 파일에 다음 환경 변수들을 설정해야 합니다:

```bash
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Notion API
NOTION_TOKEN=your_notion_token_here
NOTION_DB_ID=your_notion_database_id_here

# App Config
APP_PASSWORD=your_secure_password_here

# Public config
NEXT_PUBLIC_API_URL=https://your-domain.com
```

### 각 환경 변수 설정 방법

#### 1.1 Google Gemini API Key
1. [Google AI Studio](https://aistudio.google.com/app/apikeys) 방문
2. "API Key 만들기" 클릭
3. 생성된 API 키 복사

#### 1.2 Notion API Token
1. [Notion 개발자 페이지](https://www.notion.so/my-integrations) 방문
2. 새 통합 생성
3. 토큰 복사
4. Notion 데이터베이스에 통합 추가

#### 1.3 Notion Database ID
1. Notion에서 투자 분석 기록 데이터베이스 열기
2. URL에서 `?v=` 이전의 32자 ID 복사
3. `-` 제거 (e.g., `abcd1234-5678-90ab-cdef-1234567890ab` → `abcd12345678990abcdef1234567890ab`)

## 2. Cloudflare Pages 배포

### 2.1 Cloudflare Pages 프로젝트 생성

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) 로그인
2. **Pages** → **Connect to Git**
3. GitHub 저장소 선택: `kyunghwanchoi747/yjinvest`
4. 배포 설정:
   - **Framework**: Next.js
   - **Build command**: `npm run build`
   - **Build output directory**: `.next`
   - **Environment variables**: 아래 참고

### 2.2 환경 변수 설정 (Cloudflare)

Cloudflare Pages 프로젝트 설정에서:

1. **Settings** → **Environment variables**
2. 다음 변수들 추가 (`.env.local`과 동일):
   - `GOOGLE_API_KEY`
   - `NOTION_TOKEN`
   - `NOTION_DB_ID`
   - `APP_PASSWORD`

### 2.3 자동 배포 확인

- GitHub에 푸시하면 자동으로 Cloudflare Pages에 배포됨
- 배포 진행 상황은 Cloudflare Dashboard에서 확인 가능

## 3. 로컬 개발

### 개발 서버 시작

```bash
npm run dev
```

http://localhost:3000 에서 접속 가능

### 빌드 테스트

```bash
npm run build
npm start
```

## 4. 주요 기능

### 주식 분석 탭
- 티커 또는 회사명 입력
- 실시간 주가 데이터 조회
- AI가 생성한 종합 분석 결과
- 관련 뉴스 표시
- Notion에 분석 결과 저장

### 거시경제 지표 탭
- 한국 기준금리
- 미국 기준금리
- 원/달러 환율
- 소비자물가상승률 (CPI)
- 금리 추이 차트

## 5. API 엔드포인트

### `/api/stock?ticker=AAPL`
주가 데이터 조회
- 현재가, 전일 종가, 거래량
- 1주일 차트 데이터
- 관련 뉴스

### `/api/analyze` (POST)
AI 종합 분석 생성
- Request: `{ stockData, macroData }`
- Response: `{ insight }`

### `/api/macro`
거시경제 지표 조회

### `/api/notion` (POST)
Notion 데이터베이스에 분석 결과 저장
- Request: `{ ticker, price, summary, note }`

## 6. 트러블슈팅

### 배포 실패
- 환경 변수 확인
- 빌드 로그 확인: `npm run build`

### AI 분석이 작동하지 않음
- `GOOGLE_API_KEY` 확인
- API 사용 제한 확인

### Notion 저장 실패
- `NOTION_TOKEN` 확인
- `NOTION_DB_ID` 확인
- Notion 데이터베이스에 통합 권한 확인

## 7. 보안 참고사항

- `.env.local`은 절대 Git에 커밋하지 마세요 (.gitignore에 설정됨)
- Cloudflare에서 비밀 환경 변수 사용
- 프로덕션에서는 강력한 APP_PASSWORD 사용
