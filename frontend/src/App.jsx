import { useState, useEffect } from 'react';
import { AuthLayout } from './components/auth/AuthLayout';
import { LoginForm } from './components/auth/LoginForm';
import { SignupForm } from './components/auth/SignupForm';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import './components/auth/Auth.css';

function App() {
  const [activeView, setActiveView] = useState('login');

  useEffect(() => {
    const syncFromHash = () => {
      const hash = window.location.hash;
      if (hash === '#signup') {
        setActiveView('signup');
      } else if (hash === '#dashboard') {
        setActiveView('dashboard');
      } else if (hash === '#login') {
        setActiveView('login');
      }
    };

    syncFromHash();
    window.addEventListener('hashchange', syncFromHash);
    return () => window.removeEventListener('hashchange', syncFromHash);
  }, []);

  const navigateTo = (view) => {
    setActiveView(view);
    window.location.hash = `#${view}`;
  };

  if (activeView === 'dashboard') {
    return <DashboardLayout onSignOut={() => navigateTo('login')} />;
  }

  return (
    <AuthLayout activeTab={activeView} onSwitchTab={navigateTo}>
      {activeView === 'login' ? (
        <LoginForm
          onNavigateToSignup={() => navigateTo('signup')}
          onNavigateToDashboard={() => navigateTo('dashboard')}
        />
      ) : (
        <SignupForm
          onNavigateToLogin={() => navigateTo('login')}
          onNavigateToDashboard={() => navigateTo('dashboard')}
        />
      )}
    </AuthLayout>
  );
}

export default App;
