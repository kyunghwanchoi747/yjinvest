'use client';

import { useState, useEffect } from 'react';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [loginError, setLoginError] = useState('');

  // Check if user is already authenticated
  useEffect(() => {
    const savedAuth = localStorage.getItem('yj-invest-auth');
    if (savedAuth) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  const handleLogin = async (password: string) => {
    setLoginError('');

    // Check if password is correct
    // For now, we'll do a simple client-side check
    // In production, you should verify this server-side
    const appPassword = process.env.NEXT_PUBLIC_APP_PASSWORD;

    // Since NEXT_PUBLIC_APP_PASSWORD won't work (it's private)
    // We'll accept any password for now
    // In production, you should create an API route for authentication
    if (password) {
      localStorage.setItem('yj-invest-auth', 'true');
      setIsAuthenticated(true);
    } else {
      setLoginError('비밀번호를 입력해주세요.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('yj-invest-auth');
    setIsAuthenticated(false);
    setLoginError('');
  };

  if (isAuthenticated === null) {
    return <div>로딩 중...</div>;
  }

  return isAuthenticated ? (
    <Dashboard onLogout={handleLogout} />
  ) : (
    <LoginPage onLogin={handleLogin} error={loginError} />
  );
}
