import type { FC } from 'react'
import { Link } from '../router/Router'

export const JournalistsPage: FC = () => {
  return (
    <div className="page journalists-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 2 of 5</span>
          <h1 className="page-title">Journalist Management</h1>
          <p className="page-description">
            Upload your CSV journalist roster or view existing media contacts associated with this campaign.
          </p>
        </div>
      </div>

      <div className="page-card placeholder-card">
        <div className="placeholder-icon">👥</div>
        <h2 className="placeholder-title">Journalist Roster & CSV Import Placeholder</h2>
        <p className="placeholder-text">
          In TASK-005 and TASK-006, CSV upload validation, journalist parsing, and contact tables will be integrated here.
        </p>

        <div className="placeholder-preview">
          <div className="preview-table-header">
            <span>Name</span>
            <span>Publication</span>
            <span>Role</span>
            <span>Topics</span>
          </div>
          <div className="preview-table-row">
            <strong>Emma Smith</strong>
            <span>Tech Weekly</span>
            <span>Technology Writer</span>
            <span className="preview-tags">
              <span className="tag">AI</span>
              <span className="tag">Developer Tools</span>
            </span>
          </div>
          <div className="preview-table-row">
            <strong>John Williams</strong>
            <span>Silicon Reporter</span>
            <span>Senior Tech Editor</span>
            <span className="preview-tags">
              <span className="tag">Cybersecurity</span>
              <span className="tag">Cloud</span>
            </span>
          </div>
        </div>

        <div className="placeholder-actions">
          <Link to="/" className="btn btn-secondary">
            &larr; Back to Campaign
          </Link>
          <Link to="/analysis" className="btn btn-primary">
            Next: Run AI Relevance Analysis &rarr;
          </Link>
        </div>
      </div>
    </div>
  )
}
