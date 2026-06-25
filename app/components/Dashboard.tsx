'use client';

import { useState, useEffect } from 'react';
import StockAnalysis from './StockAnalysis';
import MacroEconomics from './MacroEconomics';
import styles from './Dashboard.module.css';

interface DashboardProps {
  onLogout: () => void;
}

export default function Dashboard({ onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<'stock' | 'macro'>('stock');

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <h1>📈 YJ INVEST - AI Private Investment Diary</h1>
          <button onClick={onLogout} className={styles.logoutButton}>
            로그아웃
          </button>
        </div>
        <p className={styles.subtitle}>
          거시경제 통계와 주식 데이터를 연동하여, AI와 함께 투자 전략을 수립하고
          기록하는 나만의 프라이빗 비서입니다.
        </p>
      </header>

      <main className={styles.main}>
        <div className={styles.tabs}>
          <button
            className={`${styles.tabButton} ${
              activeTab === 'stock' ? styles.active : ''
            }`}
            onClick={() => setActiveTab('stock')}
          >
            📊 주식 투자 분석
          </button>
          <button
            className={`${styles.tabButton} ${
              activeTab === 'macro' ? styles.active : ''
            }`}
            onClick={() => setActiveTab('macro')}
          >
            🌐 거시경제 지표
          </button>
        </div>

        {activeTab === 'stock' && <StockAnalysis />}
        {activeTab === 'macro' && <MacroEconomics />}
      </main>
    </div>
  );
}
