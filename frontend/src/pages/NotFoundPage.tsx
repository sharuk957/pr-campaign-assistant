import type { FC } from 'react'
import { Link } from '../router/Router'

export const NotFoundPage: FC = () => {
  return (
    <div className="page not-found-page">
      <div className="page-card placeholder-card">
        <div className="placeholder-icon">🔍</div>
        <h1 className="placeholder-title">Page Not Found</h1>
        <p className="placeholder-text">
          The page you requested does not exist or has been moved.
        </p>
        <div className="placeholder-actions">
          <Link to="/" className="btn btn-primary">
            Return to Campaign Setup
          </Link>
        </div>
      </div>
    </div>
  )
}
