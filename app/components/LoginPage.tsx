'use client';

import { useState } from 'react';
import styles from './LoginPage.module.css';

interface LoginPageProps {
  onLogin: (password: string) => void;
  error?: string;
}

export default function LoginPage({ onLogin, error }: LoginPageProps) {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    onLogin(password);
    setLoading(false);
  };

  return (
    <div className={styles.container}>
      <div className={styles.loginBox}>
        <h1 className={styles.title}>🔐 YJ INVEST Private Access</h1>
        <p className={styles.description}>
          허가받은 파트너만 접속 가능한 개인 투자 분석 공간입니다.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            type="password"
            placeholder="액세스 비밀번호 입력"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            className={styles.input}
          />

          {error && <p className={styles.error}>{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className={styles.button}
          >
            {loading ? '인증 중...' : '인증 및 입장하기'}
          </button>
        </form>
      </div>
    </div>
  );
}
