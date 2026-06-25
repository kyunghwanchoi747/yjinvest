'use client';

import Dashboard from './components/Dashboard';

export default function Home() {
  const handleLogout = () => {
    // Logout functionality (can be extended later)
  };

  return <Dashboard onLogout={handleLogout} />;
}
