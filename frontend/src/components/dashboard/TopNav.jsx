import { useState } from 'react';
import { Button } from '../common/Button';

export function TopNav({
  activeSectionTitle,
  searchQuery,
  onSearchChange,
  onOpenGithubModal,
  onSignOut,
}) {
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  return (
    <header className="dashboard-topnav">
      <div className="topnav-left">
        <div className="breadcrumb-trail">
          <span className="breadcrumb-root">SpecTrace</span>
          <span className="breadcrumb-separator">/</span>
          <h1 className="breadcrumb-current">{activeSectionTitle}</h1>
        </div>
      </div>

      <div className="topnav-center">
        <div className="global-search-container">
          <svg
            className="search-icon"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search requirements, commits, repos... (e.g. Stripe, REQ-104)"
            className="global-search-input"
            aria-label="Search dashboard"
          />
          {searchQuery && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => onSearchChange('')}
              aria-label="Clear search"
            >
              &times;
            </button>
          )}
        </div>
      </div>

      <div className="topnav-right">
        <Button
          variant="primary"
          className="topnav-github-btn"
          onClick={onOpenGithubModal}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
          </svg>
          <span>Connect GitHub</span>
        </Button>

        <div className="user-profile-menu-container">
          <button
            type="button"
            className="user-profile-trigger"
            onClick={() => setShowProfileMenu((prev) => !prev)}
            aria-expanded={showProfileMenu}
            aria-haspopup="true"
          >
            <div className="user-avatar" aria-hidden="true">
              AS
            </div>
            <div className="user-meta">
              <span className="user-name">Anjali Sagar</span>
              <span className="user-role">Lead Engineer</span>
            </div>
            <svg
              className={`dropdown-chevron ${showProfileMenu ? 'is-open' : ''}`}
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          {showProfileMenu && (
            <div className="user-profile-dropdown" role="menu">
              <div className="dropdown-user-header">
                <strong>Anjali Sagar</strong>
                <span>anjali@spectrace.internal</span>
              </div>
              <div className="dropdown-divider" />
              <button
                type="button"
                className="dropdown-item"
                role="menuitem"
                onClick={() => {
                  setShowProfileMenu(false);
                  onOpenGithubModal();
                }}
              >
                GitHub App Settings
              </button>
              <button
                type="button"
                className="dropdown-item"
                role="menuitem"
                onClick={() => {
                  setShowProfileMenu(false);
                  onSignOut();
                }}
              >
                Return to Login / Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
