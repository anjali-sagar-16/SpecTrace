import { RECENT_ANALYSES } from '../dashboardData';
import { Button } from '../../common/Button';

export function HistoryView({ onSelectSection }) {
  return (
    <div className="dashboard-view-content">
      <div className="view-banner">
        <div>
          <h2 className="view-heading">Change Intelligence History & Audit Logs</h2>
          <p className="view-subheading">
            Chronological audit trail of all pull requests, commit evaluations, and detected specification regressions.
          </p>
        </div>
        <Button variant="secondary">
          Download Audit Log (.json)
        </Button>
      </div>

      <div className="timeline-container">
        {RECENT_ANALYSES.map((entry) => (
          <div key={entry.id} className="timeline-item">
            <div className="timeline-marker-col">
              <div className={`timeline-dot timeline-dot--${entry.riskLevel}`} />
              <div className="timeline-line" />
            </div>

            <div className="timeline-content-card">
              <div className="timeline-card-header">
                <div className="timeline-title-group">
                  <span className="timeline-id">{entry.id}</span>
                  <strong className="timeline-req">{entry.reqId}: {entry.reqTitle}</strong>
                </div>
                <span className="timeline-time">{entry.date}</span>
              </div>

              <p className="timeline-summary">{entry.summary}</p>

              <div className="timeline-meta-row">
                <span className="meta-tag">Repo: <strong>{entry.repo}</strong></span>
                <span className="meta-tag">Branch: <code>{entry.branch}</code></span>
                <span className="meta-tag">Commit: <code>{entry.commitSha}</code></span>
                <span className="meta-tag">Author: {entry.author}</span>
                <span className={`badge-status ${entry.riskLevel === 'high' ? 'badge-high-risk' : entry.riskLevel === 'medium' ? 'badge-in-review' : 'badge-passed'}`}>
                  {entry.status}
                </span>
              </div>

              <div className="timeline-actions">
                <button
                  type="button"
                  className="table-action-btn"
                  onClick={() => onSelectSection('impact-analysis')}
                >
                  View Full Evaluation Trace &rarr;
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="view-helper-card">
        <div className="helper-icon">&bull;</div>
        <div className="helper-text">
          <strong>Immutable Audit Trail:</strong> Historical records are retained for compliance frameworks (SOC 2, ISO 27001) to trace which requirements governed specific production deployments.
        </div>
      </div>
    </div>
  );
}
