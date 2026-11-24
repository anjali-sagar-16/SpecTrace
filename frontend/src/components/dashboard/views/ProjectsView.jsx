import { PROJECTS } from '../dashboardData';
import { Button } from '../../common/Button';

export function ProjectsView({ onSelectSection }) {
  return (
    <div className="dashboard-view-content">
      <div className="view-banner">
        <div>
          <h2 className="view-heading">Software Engineering Projects</h2>
          <p className="view-subheading">
            Group repositories, architectural domains, and functional specification sets.
          </p>
        </div>
        <Button variant="primary">
          + Create New Project
        </Button>
      </div>

      <div className="projects-grid">
        {PROJECTS.map((project) => (
          <div key={project.id} className="project-card">
            <div className="project-card-header">
              <span className="project-code-badge">{project.id}</span>
              <span className="project-status-pill">{project.status}</span>
            </div>
            <h3 className="project-card-title">{project.name}</h3>
            <p className="project-card-desc">{project.description}</p>

            <div className="project-metrics-row">
              <div className="p-metric">
                <span className="p-metric-label">Repositories</span>
                <span className="p-metric-val">{project.reposCount}</span>
              </div>
              <div className="p-metric">
                <span className="p-metric-label">Specifications</span>
                <span className="p-metric-val">{project.requirementsCount}</span>
              </div>
              <div className="p-metric">
                <span className="p-metric-label">Last Evaluated</span>
                <span className="p-metric-val p-metric-val--subtle">{project.lastAnalyzed}</span>
              </div>
            </div>

            <div className="project-card-actions">
              <button
                type="button"
                className="project-action-btn"
                onClick={() => onSelectSection('requirements')}
              >
                View Specifications &rarr;
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="view-helper-card">
        <div className="helper-icon">&bull;</div>
        <div className="helper-text">
          <strong>Project Management Service:</strong> Multi-repository project grouping routes change detection across dependent services. Full project CRUD will bind to the backend project service.
        </div>
      </div>
    </div>
  );
}
