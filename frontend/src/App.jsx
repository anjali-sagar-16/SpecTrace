import { useState, useEffect } from 'react';
import { AuthLayout } from './components/auth/AuthLayout';
import { LoginForm } from './components/auth/LoginForm';
import { SignupForm } from './components/auth/SignupForm';
import './components/auth/Auth.css';

function App() {
  const [activeView, setActiveView] = useState('login');

  useEffect(() => {
    const syncFromHash = () => {
      if (window.location.hash === '#signup') {
        setActiveView('signup');
      } else if (window.location.hash === '#login') {
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

  return (
    <AuthLayout activeTab={activeView} onSwitchTab={navigateTo}>
      {activeView === 'login' ? (
        <LoginForm onNavigateToSignup={() => navigateTo('signup')} />
      ) : (
        <SignupForm onNavigateToLogin={() => navigateTo('login')} />
      )}
    </AuthLayout>
  );
}

export default App;
