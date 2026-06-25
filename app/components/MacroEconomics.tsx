'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import styles from './MacroEconomics.module.css';

interface MacroData {
  korea_base_rate: number;
  korea_base_rate_source: string;
  us_base_rate: number;
  exchange_rate: number;
  cpi_inflation: number;
  korea_base_rate_history?: {
    dates: string[];
    rates: number[];
  };
}

export default function MacroEconomics() {
  const [macroData, setMacroData] = useState<MacroData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/macro');
        if (res.ok) {
          const data = await res.json();
          setMacroData(data);
        }
      } catch (error) {
        console.error('Failed to fetch macro data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const chartData = macroData?.korea_base_rate_history
    ? macroData.korea_base_rate_history.dates.map((date, idx) => ({
        date,
        rate: macroData.korea_base_rate_history!.rates[idx],
      }))
    : [];

  if (loading) {
    return <div className={styles.loading}>데이터를 불러오는 중...</div>;
  }

  return (
    <div className={styles.container}>
      <h2>🌐 거시경제 지표 및 시장 요약</h2>
      <p className={styles.subtitle}>
        한국은행 경제통계시스템(ECOS) API 및 주요 시장 금리 지표 현황입니다.
      </p>

      {macroData && (
        <>
          <div className={styles.metrics}>
            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>한국 기준금리</div>
              <div className={styles.metricValue}>{macroData.korea_base_rate}%</div>
              <div className={styles.metricDelta}>BOK 기준</div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>미국 기준금리</div>
              <div className={styles.metricValue}>{macroData.us_base_rate}%</div>
              <div className={styles.metricDelta}>FRB 기준</div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>원/달러 환율</div>
              <div className={styles.metricValue}>
                {macroData.exchange_rate.toLocaleString()} 원
              </div>
              <div className={styles.metricDelta}>현재 시세</div>
            </div>

            <div className={styles.metricCard}>
              <div className={styles.metricLabel}>소비자물가상승률 (CPI)</div>
              <div className={styles.metricValue}>{macroData.cpi_inflation}%</div>
              <div className={styles.metricDelta}>연 기준</div>
            </div>
          </div>

          <div className={styles.info}>
            데이터 출처: {macroData.korea_base_rate_source}
          </div>

          {chartData.length > 0 && (
            <div className={styles.chartSection}>
              <h3>📈 한국은행 기준금리 추이</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="rate"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', r: 5 }}
                    activeDot={{ r: 7 }}
                    name="기준금리 (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  );
}
