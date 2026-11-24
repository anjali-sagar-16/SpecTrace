import { Logo } from '../common/Logo';

export function AuthLayout({ children, activeTab, onSwitchTab }) {
  return (
    <div className="auth-viewport">
      <header className="auth-top-nav">
        <div className="auth-top-nav-inner">
          <Logo size="medium" showTagline={true} />
          
          <nav className="auth-quick-switch" aria-label="Authentication navigation">
            <button
              type="button"
              className={`nav-tab-btn ${activeTab === 'login' ? 'is-active' : ''}`}
              onClick={() => onSwitchTab('login')}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`nav-tab-btn ${activeTab === 'signup' ? 'is-active' : ''}`}
              onClick={() => onSwitchTab('signup')}
            >
              Create Account
            </button>
            <button
              type="button"
              className={`nav-tab-btn ${activeTab === 'dashboard' ? 'is-active' : ''}`}
              onClick={() => onSwitchTab('dashboard')}
            >
              Dashboard
            </button>
          </nav>
        </div>
      </header>

      <main className="auth-main-content">
        <div className="auth-card">
          {children}
        </div>
      </main>

      <footer className="auth-footer">
        <p className="auth-footer-text">
          <strong>SpecTrace</strong> &mdash; AI-Powered Software Change Intelligence Platform
        </p>
        <p className="auth-footer-subtext">
          Helping developers analyze requirement changes and their codebase impact.
        </p>
      </footer>
    </div>
  );
}
