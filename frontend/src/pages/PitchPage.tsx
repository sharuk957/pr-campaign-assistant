import type { FC } from 'react'
import { Link } from '../router/Router'

export const PitchPage: FC = () => {
  return (
    <div className="page pitch-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 5 of 5</span>
          <h1 className="page-title">Personalized Pitch Outreach</h1>
          <p className="page-description">
            Review, regenerate, and copy custom outreach pitches tailored to individual journalists and grounded in campaign themes.
          </p>
        </div>
      </div>

      <div className="page-card placeholder-card">
        <div className="placeholder-icon">✉️</div>
        <h2 className="placeholder-title">Personalized Pitch Generation Placeholder</h2>
        <p className="placeholder-text">
          In TASK-011, automated pitch generation, regeneration, and one-click clipboard copying will be implemented here.
        </p>

        <div className="placeholder-preview pitch-preview-box">
          <div className="pitch-subject">
            <strong>Subject:</strong> Python security platform research for your developer tooling coverage
          </div>
          <div className="pitch-body">
            <p>Hi Emma,</p>
            <p>
              I saw your recent coverage on AI developer tools and Python security. Given Acme Security's launch of our automated vulnerability detection platform for Python developers, I thought this might be a compelling story for your readers at Tech Weekly...
            </p>
          </div>
        </div>

        <div className="placeholder-actions">
          <Link to="/journalists/details" className="btn btn-secondary">
            &larr; Back to Journalist Details
          </Link>
          <Link to="/" className="btn btn-primary">
            Start New Campaign
          </Link>
        </div>
      </div>
    </div>
  )
}
