import type { FC } from 'react'
import { Link } from '../router/Router'

export const JournalistDetailsPage: FC = () => {
  return (
    <div className="page journalist-details-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 4 of 5</span>
          <h1 className="page-title">Journalist Profile & Evidence</h1>
          <p className="page-description">
            Deep dive into journalist bio, recent coverage, AI match reasoning, and grounded evidence.
          </p>
        </div>
      </div>

      <div className="page-card placeholder-card">
        <div className="placeholder-icon">🔍</div>
        <h2 className="placeholder-title">Journalist Details Placeholder</h2>
        <p className="placeholder-text">
          In TASK-010 and TASK-012, detailed source profiles alongside validated AI explanations will be displayed here.
        </p>

        <div className="placeholder-preview">
          <div className="detail-split">
            <div className="detail-pane">
              <h3>Source Information</h3>
              <p><strong>Name:</strong> Emma Smith</p>
              <p><strong>Publication:</strong> Tech Weekly</p>
              <p><strong>Role:</strong> Technology Writer</p>
              <p><strong>Topics:</strong> AI, Developer Tools, Python</p>
            </div>
            <div className="detail-pane ai-pane">
              <h3>AI Relevance Breakdown</h3>
              <p><strong>Score:</strong> 92 (High Priority)</p>
              <p><strong>Reasons:</strong> Covers developer tooling ecosystem and AI automation.</p>
              <p><strong>Evidence:</strong> Recent article on "AI coding tools & Python security".</p>
            </div>
          </div>
        </div>

        <div className="placeholder-actions">
          <Link to="/analysis" className="btn btn-secondary">
            &larr; Back to Analysis
          </Link>
          <Link to="/pitch" className="btn btn-primary">
            Next: Generate Outreach Pitch &rarr;
          </Link>
        </div>
      </div>
    </div>
  )
}
