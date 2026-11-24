import { REPOSITORIES } from '../dashboardData';
import { Button } from '../../common/Button';

export function RepositoriesView({ onOpenGithubModal, onSelectSection }) {
  return (
    <div className="dashboard-view-content">
      <div className="view-banner">
        <div>
          <h2 className="view-heading">Connected Code Repositories</h2>
          <p className="view-subheading">
            Repositories with active AST tracing, PR webhooks, and requirement mappings.
          </p>
        </div>
        <Button variant="primary" onClick={onOpenGithubModal}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
          </svg>
          <span>Connect New Repository</span>
        </Button>
      </div>

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Repository</th>
              <th>Language Stack</th>
              <th>Tracked Branch</th>
              <th>Sync Health</th>
              <th>Mapped Specs</th>
              <th>Active Alerts</th>
              <th>Last AST Sync</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {REPOSITORIES.map((repo) => (
              <tr key={repo.id}>
                <td>
                  <div className="repo-table-cell">
                    <span className="repo-table-title">{repo.name}</span>
                    <span className="repo-table-fullname">{repo.fullName}</span>
                  </div>
                </td>
                <td>
                  <span className="repo-lang-badge">{repo.language}</span>
                </td>
                <td>
                  <code>{repo.defaultBranch}</code>
                </td>
                <td>
                  <span className="sync-status-badge">
                    <span className="sync-dot" />
                    {repo.status}
                  </span>
                </td>
                <td>
                  <strong>{repo.requirementsCount}</strong>
                </td>
                <td>
                  {repo.openImpacts > 0 ? (
                    <span className="badge-status badge-high-risk">
                      {repo.openImpacts} Alert
                    </span>
                  ) : (
                    <span className="badge-status badge-passed">0 Alerts</span>
                  )}
                </td>
                <td>
                  <span className="time-text">{repo.lastSync}</span>
                </td>
                <td>
                  <button
                    type="button"
                    className="table-action-btn"
                    onClick={() => onSelectSection('impact-analysis')}
                  >
                    View Traces
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="view-helper-card">
        <div className="helper-icon">&bull;</div>
        <div className="helper-text">
          <strong>GitHub Webhook Ingestion:</strong> Pull request webhooks notify SpecTrace of pushed commits. AST parsing runs incrementally on changed modules only.
        </div>
      </div>
    </div>
  );
}
