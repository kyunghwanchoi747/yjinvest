# 📈 YJ INVEST - AI Private Investment Diary

거시경제 통계와 주식 데이터를 연동하여, AI와 함께 투자 전략을 수립하고 Notion에 기록하는 나만의 프라이빗 투자 분석 플랫폼입니다.

## 🎯 주요 기능

### 📊 주식 투자 분석
- **실시간 주가 데이터**: Yahoo Finance API를 통한 실시간 주가, 거래량, 시장 정보
- **1주일 차트**: 캔들스틱 차트로 주가 추이 시각화
- **AI 분석**: Google Gemini를 활용한 거시경제 + 주식 종합 분석
- **관련 뉴스**: 종목 관련 최신 뉴스 자동 수집
- **Notion 통합**: 분석 결과를 Notion 데이터베이스에 자동 저장

### 🌐 거시경제 지표
- 한국 기준금리 (한국은행)
- 미국 기준금리 (연방준비제도)
- 원/달러 환율
- 소비자물가상승률 (CPI)
- 금리 추이 차트

### 🔐 보안
- 비밀번호 기반 프라이빗 모드
- 로컬스토리지를 통한 세션 관리
- API 키는 서버 측에서만 관리 (클라이언트 노출 없음)

## 🚀 시작하기

### 필수 요구사항
- Node.js 18+
- npm 또는 yarn

### 설치

```bash
npm install
```

### 환경 설정

`.env.local` 파일 생성:

```bash
GOOGLE_API_KEY=your_gemini_api_key
NOTION_TOKEN=your_notion_token
NOTION_DB_ID=your_notion_database_id
APP_PASSWORD=your_secure_password
NEXT_PUBLIC_API_URL=http://localhost:3000
```

자세한 설정 방법은 [DEPLOYMENT.md](./DEPLOYMENT.md) 참고

### 개발 서버 실행

```bash
npm run dev
```

http://localhost:3000 에서 접속

### 빌드

```bash
npm run build
npm start
```

## 📁 프로젝트 구조

```
.
├── app/
│   ├── api/                    # API 라우트
│   │   ├── stock/route.ts      # 주가 데이터 API
│   │   ├── analyze/route.ts    # AI 분석 API
│   │   ├── macro/route.ts      # 거시경제 데이터 API
│   │   └── notion/route.ts     # Notion 저장 API
│   ├── components/             # React 컴포넌트
│   │   ├── LoginPage.tsx       # 로그인 페이지
│   │   ├── Dashboard.tsx       # 대시보드
│   │   ├── StockAnalysis.tsx   # 주식 분석 탭
│   │   └── MacroEconomics.tsx  # 거시경제 탭
│   ├── layout.tsx              # 루트 레이아웃
│   ├── page.tsx                # 메인 페이지
│   └── globals.css             # 글로벌 스타일
├── public/                     # 정적 파일
├── package.json                # 프로젝트 설정
├── tsconfig.json               # TypeScript 설정
├── next.config.ts              # Next.js 설정
└── DEPLOYMENT.md               # 배포 가이드
```

## 🛠️ 기술 스택

- **Frontend**: React 19 + TypeScript
- **Framework**: Next.js 16
- **Styling**: CSS Modules
- **Charts**: Recharts
- **APIs**:
  - [Yahoo Finance 2](https://github.com/gaijinx/yahoo-finance2) - 주가 데이터
  - [Google Generative AI](https://ai.google.dev/) - AI 분석
  - [Notion API](https://developers.notion.com/) - 데이터 저장
- **Deployment**: Cloudflare Pages

## 📡 API 통합

### Yahoo Finance
- 실시간 주가 데이터
- 1주일 역사 데이터
- 관련 뉴스

### Google Gemini 2.0 Flash
- 주가 및 거시경제 종합 분석
- 한국어 지원
- 빠른 응답 속도

### Notion
- 분석 결과 저장
- 투자자 메모 기록
- 데이터베이스 자동 관리

## 🌍 배포

Cloudflare Pages를 사용한 자동 배포:

1. GitHub에 푸시 → 자동으로 Cloudflare에 배포
2. 빌드 시간: ~2분
3. 전 세계 CDN으로 빠른 속도

자세한 배포 방법은 [DEPLOYMENT.md](./DEPLOYMENT.md) 참고

## 📝 라이선스

개인 프로젝트

## 👨‍💼 기여

현재는 개인 프로젝트입니다.

---

**주의**: 이 플랫폼은 교육 목적용입니다. 투자 결정 시에는 전문가의 상담을 받으세요.
