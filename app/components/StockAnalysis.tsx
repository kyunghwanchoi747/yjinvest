'use client';

import { useState } from 'react';
import {
  LineChart,
  Line,
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import styles from './StockAnalysis.module.css';

interface StockData {
  ticker: string;
  shortName: string;
  currentPrice: number;
  previousClose: number;
  volume: number;
  marketCap?: number;
  pe?: number;
  fiftyTwoWeekHigh?: number;
  fiftyTwoWeekLow?: number;
  historical: Array<{
    date: Date;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  news: Array<{
    title: string;
    link: string;
    publisher: string;
  }>;
}

interface MacroData {
  korea_base_rate: number;
  us_base_rate: number;
  exchange_rate: number;
  cpi_inflation: number;
}

export default function StockAnalysis() {
  const [ticker, setTicker] = useState('AAPL');
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [macroData, setMacroData] = useState<MacroData | null>(null);
  const [insight, setInsight] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [note, setNote] = useState('');

  const handleSearch = async () => {
    if (!ticker.trim()) {
      setError('티커를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setInsight('');

    try {
      // Fetch stock data
      const stockRes = await fetch(
        `/api/stock?ticker=${encodeURIComponent(ticker)}`
      );
      if (!stockRes.ok) throw new Error('주식 데이터를 가져올 수 없습니다.');
      const stock = await stockRes.json();
      setStockData(stock);

      // Fetch macro data
      const macroRes = await fetch('/api/macro');
      if (!macroRes.ok) throw new Error('거시경제 데이터를 가져올 수 없습니다.');
      const macro = await macroRes.json();
      setMacroData(macro);

      // Generate analysis
      const analysisRes = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stockData: stock, macroData: macro }),
      });
      if (!analysisRes.ok) throw new Error('분석을 생성할 수 없습니다.');
      const { insight: analysisInsight } = await analysisRes.json();
      setInsight(analysisInsight);
    } catch (err: any) {
      setError(err.message || '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToNotion = async () => {
    if (!stockData) {
      setError('먼저 주식을 검색해주세요.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('/api/notion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker: stockData.ticker,
          price: stockData.currentPrice,
          summary: insight,
          note: note,
        }),
      });

      if (!res.ok) throw new Error('Notion 저장에 실패했습니다.');
      alert('✅ Notion에 저장되었습니다!');
      setNote('');
    } catch (err: any) {
      setError(err.message || 'Notion 저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const chartData = stockData?.historical
    ? stockData.historical.map((day: any) => ({
        date: new Date(day.date).toLocaleDateString('ko-KR', {
          month: 'short',
          day: 'numeric',
        }),
        open: day.open,
        high: day.high,
        low: day.low,
        close: day.close,
        volume: day.volume,
      }))
    : [];

  const priceChange = stockData
    ? stockData.currentPrice - stockData.previousClose
    : 0;
  const priceChangePercent = stockData
    ? (priceChange / stockData.previousClose) * 100
    : 0;

  return (
    <div className={styles.container}>
      <div className={styles.sidebar}>
        <div className={styles.searchCard}>
          <h3>🔍 종목 분석</h3>
          <input
            type="text"
            placeholder="티커 또는 회사명 (예: AAPL, 테슬라)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            disabled={loading}
            className={styles.input}
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className={styles.button}
          >
            {loading ? '분석 중...' : '분석 시작'}
          </button>

          <details className={styles.helpDetails}>
            <summary>ℹ️ 티커 입력 도움말</summary>
            <ul>
              <li>
                <strong>AI가 자동으로 티커를 찾아줍니다!</strong>
              </li>
              <li>한글 종목명: 테슬라, 삼성전자, 엔비디아 등</li>
              <li>영문 티커: AAPL, TSLA, NVDA</li>
              <li>한국 주식 티커: 005930.KS (코스피), 035720.KQ (코스닥)</li>
            </ul>
          </details>

          <div className={styles.securityStatus}>
            <p>🔑 보안 연결 상태</p>
            <p className={styles.privateMode}>프라이빗 모드 활성화됨</p>
          </div>
        </div>
      </div>

      <div className={styles.main}>
        {error && <div className={styles.alert + ' ' + styles.error}>{error}</div>}

        {stockData && (
          <>
            <div className={styles.header}>
              <h2>
                {stockData.shortName} ({stockData.ticker})
              </h2>
            </div>

            <div className={styles.metrics}>
              <div className={styles.metricCard}>
                <div className={styles.metricLabel}>현재가</div>
                <div className={styles.metricValue}>
                  ${stockData.currentPrice.toFixed(2)}
                </div>
                <div
                  className={
                    styles.metricDelta +
                    ' ' +
                    (priceChange >= 0 ? styles.positive : styles.negative)
                  }
                >
                  {priceChange >= 0 ? '▲' : '▼'} {Math.abs(priceChange).toFixed(
                    2
                  )} ({Math.abs(priceChangePercent).toFixed(2)}%)
                </div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricLabel}>전일 종가</div>
                <div className={styles.metricValue}>
                  ${stockData.previousClose.toFixed(2)}
                </div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricLabel}>거래량</div>
                <div className={styles.metricValue}>
                  {(stockData.volume / 1000000).toFixed(1)}M
                </div>
              </div>

              {stockData.pe && (
                <div className={styles.metricCard}>
                  <div className={styles.metricLabel}>P/E 비율</div>
                  <div className={styles.metricValue}>
                    {stockData.pe.toFixed(2)}
                  </div>
                </div>
              )}
            </div>

            <div className={styles.content}>
              <div className={styles.chartSection}>
                <h3>🕯️ 주가 1주일 차트</h3>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Bar
                        yAxisId="left"
                        dataKey="close"
                        fill="#3b82f6"
                        name="Close Price"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="volume"
                        stroke="#ef4444"
                        name="Volume"
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                ) : (
                  <p>차트 데이터 없음</p>
                )}
              </div>

              <div className={styles.analysisSection}>
                <h3>🤖 AI 거시경제 + 주식 종합 분석</h3>
                {insight ? (
                  <div className={styles.analysisContent}>{insight}</div>
                ) : (
                  <p className={styles.placeholder}>분석 결과를 기다리는 중...</p>
                )}

                <h3 style={{ marginTop: '24px' }}>📰 관련 최근 뉴스</h3>
                {stockData.news && stockData.news.length > 0 ? (
                  <ul className={styles.newsList}>
                    {stockData.news.map((item, idx) => (
                      <li key={idx}>
                        <a href={item.link} target="_blank" rel="noopener">
                          {item.title}
                        </a>
                        <span className={styles.publisher}>{item.publisher}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className={styles.placeholder}>관련 뉴스 없음</p>
                )}
              </div>
            </div>

            <div className={styles.notionSection}>
              <h3>📝 Notion에 분석 결과 기록</h3>
              <textarea
                placeholder="투자자 개인 메모 (선택사항)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className={styles.textarea}
              />
              <button
                onClick={handleSaveToNotion}
                disabled={loading}
                className={styles.buttonPrimary}
              >
                {loading ? '저장 중...' : '💾 Notion 저장'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
