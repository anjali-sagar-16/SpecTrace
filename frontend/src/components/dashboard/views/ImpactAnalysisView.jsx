import { IMPACT_SAMPLE_DETAILS } from '../dashboardData';
import { Button } from '../../common/Button';

export function ImpactAnalysisView({ onSelectSection }) {
  const data = IMPACT_SAMPLE_DETAILS;

  return (
    <div className="dashboard-view-content">
      <div className="view-banner">
        <div>
          <div className="impact-breadcrumb-tag">Live Impact Assessment</div>
          <h2 className="view-heading">{data.requirementId}: {data.title}</h2>
          <p className="view-subheading">
            AI-evaluated impact graph showing how this requirement modification ripples across services.
          </p>
        </div>
        <div className="banner-actions-group">
          <Button
            variant="ghost"
            onClick={() => onSelectSection('requirements')}
          >
            &larr; All Requirements
          </Button>
          <Button variant="primary">
            Export Report
          </Button>
        </div>
      </div>

      {/* Impact Assessment Card */}
      <div className="impact-summary-card">
        <div className="impact-summary-top">
          <div className="risk-score-badge">
            <span className="risk-indicator" />
            <span className="risk-text">{data.riskScore}</span>
          </div>
          <span className="analyzed-timestamp">{data.analyzedAt}</span>
        </div>
        <p className="impact-summary-desc">{data.summary}</p>
      </div>

      {/* Visual Dependency Ripple Graph Representation */}
      <section className="impact-graph-section">
        <h3 className="section-title">Architectural Impact Flow</h3>
        <p className="section-subtitle">
          Downstream AST traces detected across service boundaries and database migrations.
        </p>

        <div className="architecture-flow-diagram">
          <div className="flow-node flow-node--source">
            <span className="flow-node-type">Specification Change</span>
            <strong className="flow-node-title">REQ-104 (Stripe v3)</strong>
            <span className="flow-node-meta">PRD Section 4.2</span>
          </div>

          <div className="flow-arrow">&rarr;</div>

          <div className="flow-node flow-node--danger">
            <span className="flow-node-type">API Gateway (Breaking)</span>
            <strong className="flow-node-title">payment-gateway</strong>
            <span className="flow-node-meta">3 Endpoints Affected</span>
          </div>

          <div className="flow-arrow">&rarr;</div>

          <div className="flow-node flow-node--warning">
            <span className="flow-node-type">Schema Migration</span>
            <strong className="flow-node-title">0042_payment_intent.sql</strong>
            <span className="flow-node-meta">1 Non-nullable Column</span>
          </div>

          <div className="flow-arrow">&rarr;</div>

          <div className="flow-node flow-node--client">
            <span className="flow-node-type">Frontend Client</span>
            <strong className="flow-node-title">spectrace-core (UI)</strong>
            <span className="flow-node-meta">2 Components Updated</span>
          </div>
        </div>
      </section>

      {/* Layer-by-layer breakdown */}
      <section className="impact-breakdown-section">
        <h3 className="section-title">Detailed Service Impact Breakdown</h3>
        <div className="impact-layers-list">
          {data.affectedLayers.map((layer) => (
            <div key={layer.layer} className="impact-layer-card">
              <div className="layer-header">
                <h4 className="layer-title">{layer.layer}</h4>
                <span className={`layer-badge layer-badge--${layer.statusType}`}>
                  {layer.status}
                </span>
              </div>
              <ul className="layer-items-list">
                {layer.items.map((item, idx) => (
                  <li key={idx} className="layer-item">
                    <code>{item}</code>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Recommended Engineering Actions */}
      <section className="remediation-section">
        <h3 className="section-title">Recommended Engineering Actions</h3>
        <div className="remediation-box">
          <ul className="remediation-list">
            <li>
              <strong>Update Webhook Verifier:</strong> Add support for Stripe v3 signature headers before enabling customer-facing traffic.
            </li>
            <li>
              <strong>Execute Migration in Staging:</strong> Run <code>migrations/0042_add_payment_intent_status.sql</code> on the staging cluster and verify replica sync latency.
            </li>
            <li>
              <strong>Verify Integration Tests:</strong> Run payment checkout e2e suite (<code>npm run test:e2e:checkout</code>) to ensure 3D Secure fallback works.
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}
