import { REQUIREMENTS } from '../dashboardData';
import { Button } from '../../common/Button';

export function RequirementsView({ onSelectSection }) {
  const getBadgeClass = (statusType) => {
    switch (statusType) {
      case 'warning':
        return 'badge-status badge-high-risk';
      case 'info':
        return 'badge-status badge-in-review';
      case 'success':
        return 'badge-status badge-passed';
      default:
        return 'badge-status';
    }
  };

  return (
    <div className="dashboard-view-content">
      <div className="view-banner">
        <div>
          <h2 className="view-heading">Software Requirements & Specifications</h2>
          <p className="view-subheading">
            Functional specs tracked for codebase compliance, AST node linkages, and drift detection.
          </p>
        </div>
        <Button variant="primary">
          + Import Specification
        </Button>
      </div>

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Requirement ID</th>
              <th>Specification Title</th>
              <th>Source / PRD</th>
              <th>Priority</th>
              <th>Mapped Components</th>
              <th>Compliance Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {REQUIREMENTS.map((req) => (
              <tr key={req.id}>
                <td>
                  <span className="req-id">{req.id}</span>
                </td>
                <td>
                  <span className="req-title-bold">{req.title}</span>
                </td>
                <td>
                  <span className="source-tag">{req.source}</span>
                </td>
                <td>
                  <span className="priority-badge">{req.priority}</span>
                </td>
                <td>
                  <div className="components-tags">
                    {req.components.map((comp) => (
                      <span key={comp} className="component-tag">
                        {comp}
                      </span>
                    ))}
                  </div>
                </td>
                <td>
                  <span className={getBadgeClass(req.statusType)}>
                    {req.status}
                  </span>
                </td>
                <td>
                  <button
                    type="button"
                    className="table-action-btn"
                    onClick={() => onSelectSection('impact-analysis')}
                  >
                    Trace Impact
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
          <strong>Requirement Ingestion Adapters:</strong> Supports Markdown PRDs in git repositories, Jira issues, OpenAPI schemas, and Notion requirement boards.
        </div>
      </div>
    </div>
  );
}
