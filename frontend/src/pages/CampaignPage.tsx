import type { FC } from 'react'
import { Link } from '../router/Router'

export const CampaignPage: FC = () => {
  return (
    <div className="page campaign-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 1 of 5</span>
          <h1 className="page-title">Campaign Management</h1>
          <p className="page-description">
            Define your campaign goals, company context, key topics, and target audience to anchor your outreach.
          </p>
        </div>
      </div>

      <div className="page-card placeholder-card">
        <div className="placeholder-icon">📋</div>
        <h2 className="placeholder-title">Campaign Form Placeholder</h2>
        <p className="placeholder-text">
          In TASK-004, the interactive campaign creation form and persistence layer will be implemented here.
        </p>

        <div className="placeholder-preview">
          <div className="preview-field-group">
            <span className="preview-label">Campaign Name:</span>
            <span className="preview-value">AI Developer Security Platform Launch (Sample)</span>
          </div>
          <div className="preview-field-group">
            <span className="preview-label">Target Audience:</span>
            <span className="preview-value">Software engineers, DevOps leads, Tech journalists</span>
          </div>
          <div className="preview-field-group">
            <span className="preview-label">Key Topics:</span>
            <span className="preview-tags">
              <span className="tag">AI</span>
              <span className="tag">Developer Tools</span>
              <span className="tag">Cybersecurity</span>
              <span className="tag">Python</span>
            </span>
          </div>
        </div>

        <div className="placeholder-actions">
          <Link to="/journalists" className="btn btn-primary">
            Next: Import Journalists &rarr;
          </Link>
        </div>
      </div>
    </div>
  )
}
