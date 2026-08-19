import type { FC } from 'react'
import { Link } from '../router/Router'

export const AnalysisPage: FC = () => {
  return (
    <div className="page analysis-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 3 of 5</span>
          <h1 className="page-title">Relevance Analysis & Rankings</h1>
          <p className="page-description">
            AI-driven relevance scores, priority rankings, and supporting evidence matching journalists to campaign themes.
          </p>
        </div>
      </div>

      <div className="page-card placeholder-card">
        <div className="placeholder-icon">🎯</div>
        <h2 className="placeholder-title">Analysis Results Placeholder</h2>
        <p className="placeholder-text">
          In TASK-009 and TASK-010, AI relevance evaluation, ranking cards, evidence badges, and score filters will be implemented here.
        </p>

        <div className="placeholder-preview">
          <div className="preview-ranking-item">
            <div className="ranking-badge high">92 / 100 &bull; High Priority</div>
            <div className="ranking-info">
              <strong>Emma Smith &mdash; Tech Weekly</strong>
              <p>Strong match: Regularly covers AI, Python tooling, and developer infrastructure.</p>
            </div>
            <Link to="/journalists/details" className="btn btn-sm btn-secondary">
              View Details &rarr;
            </Link>
          </div>
          <div className="preview-ranking-item">
            <div className="ranking-badge high">88 / 100 &bull; High Priority</div>
            <div className="ranking-info">
              <strong>John Williams &mdash; Silicon Reporter</strong>
              <p>Relevant coverage on developer security and enterprise application defenses.</p>
            </div>
            <Link to="/journalists/details" className="btn btn-sm btn-secondary">
              View Details &rarr;
            </Link>
          </div>
        </div>

        <div className="placeholder-actions">
          <Link to="/journalists" className="btn btn-secondary">
            &larr; Back to Journalists
          </Link>
          <Link to="/journalists/details" className="btn btn-primary">
            Next: Review Journalist Details &rarr;
          </Link>
        </div>
      </div>
    </div>
  )
}
