import { useState } from 'react';
import { Button } from '../common/Button';
import { Alert } from '../common/Alert';

export function ConnectGithubModal({ isOpen, onClose }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusNotice, setStatusNotice] = useState(null);

  if (!isOpen) return null;

  const handleAuthorize = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setStatusNotice({
        title: 'Backend OAuth Endpoint Pending',
        message: 'The frontend GitHub App handoff is prepared. When the backend service is running, this triggers the GitHub App installation flow at GET /api/v1/integrations/github/connect.',
      });
    }, 400);
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="github-modal-title">
      <div className="modal-dialog">
        <div className="modal-header">
          <div className="modal-title-group">
            <div className="github-icon-badge" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
            </div>
            <div>
              <h2 id="github-modal-title" className="modal-heading">Connect GitHub Workspace</h2>
              <p className="modal-subheading">Sync repositories and automate software change intelligence.</p>
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose} aria-label="Close dialog">
            &times;
          </button>
        </div>

        <div className="modal-body">
          {statusNotice && (
            <Alert type="info" title={statusNotice.title} onClose={() => setStatusNotice(null)}>
              {statusNotice.message}
            </Alert>
          )}

          <div className="permissions-box">
            <h3 className="permissions-title">Requested Permissions & Scopes</h3>
            <ul className="permissions-list">
              <li>
                <strong>Repository Contents (Read-only):</strong> Parse code ASTs, dependency manifests, and diff changes.
              </li>
              <li>
                <strong>Pull Request Webhooks:</strong> Trigger real-time impact evaluation when developers open or update PRs.
              </li>
              <li>
                <strong>Checks API (Write):</strong> Post automated change impact summaries directly into GitHub pull requests.
              </li>
            </ul>
          </div>

          <div className="integration-note">
            <p>
              SpecTrace does not store your source code. Analysis operates via localized AST tracing and requirement graph mapping.
            </p>
          </div>
        </div>

        <div className="modal-footer">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            loading={isSubmitting}
            onClick={handleAuthorize}
          >
            Authorize SpecTrace GitHub App
          </Button>
        </div>
      </div>
    </div>
  );
}
