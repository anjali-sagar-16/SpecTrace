import { METRICS, RECENT_ANALYSES, REPOSITORIES } from '../dashboardData';
import { Button } from '../../common/Button';

export function OverviewView({
  searchQuery,
  onOpenGithubModal,
  onSelectSection,
}) {
  const query = searchQuery.trim().toLowerCase();

  const filteredAnalyses = RECENT_ANALYSES.filter((item) => {
    if (!query) return true;
    return (
      item.reqId.toLowerCase().includes(query) ||
      item.reqTitle.toLowerCase().includes(query) ||
      item.repo.toLowerCase().includes(query) ||
      item.author.toLowerCase().includes(query) ||
      item.status.toLowerCase().includes(query)
    );
  });

  const filteredRepos = REPOSITORIES.filter((repo) => {
    if (!query) return true;
    return (
      repo.name.toLowerCase().includes(query) ||
      repo.language.toLowerCase().includes(query)
    );
  });

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'High Impact':
        return 'badge-status badge-high-risk';
      case 'In Review':
        return 'badge-status badge-in-review';
      case 'Passed':
        return 'badge-status badge-passed';
      default:
        return 'badge-status';
    }
  };

  return (
    <div className="dashboard-view-content">
      {/* Overview Metrics Cards */}
      <section className="metrics-grid" aria-label="Key Platform Metrics">
        {METRICS.map((metric) => (
          <div key={metric.id} className="metric-card">
            <span className="metric-label">{metric.label}</span>
            <div className="metric-value-row">
              <span className="metric-value">{metric.value}</span>
              <span className={`metric-change metric-change--${metric.changeType}`}>
                {metric.change}
              </span>
            </div>
            <span className="metric-subtext">{metric.subtext}</span>
          </div>
        ))}
      </section>

      {/* Getting Started Guide */}
      <section className="getting-started-banner">
        <div className="getting-started-header">
          <div className="getting-started-tag">Getting Started</div>
          <h2 className="getting-started-title">
            Specification Change Intelligence in 3 Steps
          </h2>
          <p className="getting-started-desc">
            SpecTrace maps software requirements directly to AST code nodes, detecting downstream breakage before PRs merge.
          </p>
        </div>

        <div className="getting-started-steps">
          <div className="step-card">
            <span className="step-number">01</span>
            <h3 className="step-heading">Connect Repositories</h3>
            <p className="step-text">Install the GitHub App to let SpecTrace parse code ASTs and webhook events.</p>
            <button
              type="button"
              className="step-action-link"
              onClick={onOpenGithubModal}
            >
              Connect GitHub &rarr;
            </button>
          </div>

          <div className="step-card">
            <span className="step-number">02</span>
            <h3 className="step-heading">Map Requirements</h3>
            <p className="step-text">Sync software specs from PRDs, OpenAPI schemas, or Jira issue trackers.</p>
            <button
              type="button"
              className="step-action-link"
              onClick={() => onSelectSection('requirements')}
            >
              View Requirements &rarr;
            </button>
          </div>

          <div className="step-card">
            <span className="step-number">03</span>
            <h3 className="step-heading">Automate Impact Tracing</h3>
            <p className="step-text">Get automated risk scores, contract drift alerts, and impacted test suites.</p>
            <button
              type="button"
              className="step-action-link"
              onClick={() => onSelectSection('impact-analysis')}
            >
              Inspect Impact Graph &rarr;
            </button>
          </div>
        </div>
      </section>

      {/* Recent Change Analyses */}
      <section className="dashboard-section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Recent Change Analyses</h2>
            <p className="section-subtitle">
              Real-time evaluations comparing git diffs against registered specification models.
            </p>
          </div>
          <Button
            variant="secondary"
            onClick={() => onSelectSection('impact-analysis')}
          >
            Open Impact Graph
          </Button>
        </div>

        {filteredAnalyses.length === 0 ? (
          <div className="empty-state-card">
            <div className="empty-state-icon">&empty;</div>
            <h3 className="empty-state-title">No matching change analyses</h3>
            <p className="empty-state-desc">
              No results found for &ldquo;{searchQuery}&rdquo;. Try searching by requirement ID (e.g. REQ-104), repository, or status.
            </p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Requirement</th>
                  <th>Repository & Branch</th>
                  <th>Commit / Author</th>
                  <th>Impact Status</th>
                  <th>Scope Affected</th>
                  <th>Time</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredAnalyses.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="req-cell">
                        <span className="req-id">{item.reqId}</span>
                        <span className="req-title" title={item.reqTitle}>
                          {item.reqTitle}
                        </span>
                      </div>
                    </td>
                    <td>
                      <div className="repo-cell">
                        <span className="repo-name">{item.repo}</span>
                        <span className="branch-tag">{item.branch}</span>
                      </div>
                    </td>
                    <td>
                      <div className="commit-cell">
                        <code className="commit-sha">{item.commitSha}</code>
                        <span className="commit-author">{item.author}</span>
                      </div>
                    </td>
                    <td>
                      <span className={getStatusBadgeClass(item.status)}>
                        {item.status}
                      </span>
                    </td>
                    <td>
                      <div className="scope-cell">
                        <span>{item.affectedFiles} files</span>
                        {item.impactedEndpoints > 0 && (
                          <span className="endpoint-warning">
                            {item.impactedEndpoints} API endpoints
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="time-text">{item.date}</span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="table-action-btn"
                        onClick={() => onSelectSection('impact-analysis')}
                        title="View impact trace breakdown"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Connected Repositories Grid */}
      <section className="dashboard-section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Connected Repositories</h2>
            <p className="section-subtitle">
              Active repositories synced for change tracking and requirement AST mapping.
            </p>
          </div>
          <Button variant="primary" onClick={onOpenGithubModal}>
            + Connect Repository
          </Button>
        </div>

        {filteredRepos.length === 0 ? (
          <div className="empty-state-card">
            <div className="empty-state-icon">&empty;</div>
            <h3 className="empty-state-title">No matching repositories</h3>
            <p className="empty-state-desc">
              No repositories match your search filter.
            </p>
          </div>
        ) : (
          <div className="repos-grid">
            {filteredRepos.map((repo) => (
              <div key={repo.id} className="repo-card">
                <div className="repo-card-top">
                  <div className="repo-title-row">
                    <svg
                      className="repo-svg-icon"
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <line x1="6" y1="3" x2="6" y2="15" />
                      <circle cx="18" cy="6" r="3" />
                      <circle cx="6" cy="18" r="3" />
                      <path d="M18 9a9 9 0 0 1-9 9" />
                    </svg>
                    <span className="repo-card-name">{repo.name}</span>
                  </div>
                  <span className="repo-status-pill">{repo.status}</span>
                </div>

                <div className="repo-card-meta">
                  <span className="repo-lang-tag">{repo.language}</span>
                  <span className="repo-branch-meta">Branch: <code>{repo.defaultBranch}</code></span>
                </div>

                <div className="repo-card-stats">
                  <div className="repo-stat">
                    <span className="stat-label">Mapped Specs</span>
                    <span className="stat-value">{repo.requirementsCount}</span>
                  </div>
                  <div className="repo-stat">
                    <span className="stat-label">Open Alerts</span>
                    <span className={`stat-value ${repo.openImpacts > 0 ? 'stat-alert' : ''}`}>
                      {repo.openImpacts}
                    </span>
                  </div>
                  <div className="repo-stat">
                    <span className="stat-label">Last Sync</span>
                    <span className="stat-value-subtle">{repo.lastSync}</span>
                  </div>
                </div>

                <div className="repo-card-footer">
                  <button
                    type="button"
                    className="repo-footer-btn"
                    onClick={() => onSelectSection('repositories')}
                  >
                    Manage Repository &rarr;
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
