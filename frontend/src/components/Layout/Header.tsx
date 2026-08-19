import { useCallback, useEffect, useState, type FC } from 'react'
import { checkBackendHealth } from '../../services/api'
import { Link } from '../../router'

export const Header: FC = () => {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')

  const verifyHealth = useCallback(() => {
    checkBackendHealth()
      .then((res) => {
        if (res.status === 'ok') {
          setBackendStatus('online')
        } else {
          setBackendStatus('offline')
        }
      })
      .catch(() => {
        setBackendStatus('offline')
      })
  }, [])

  useEffect(() => {
    verifyHealth()
    const interval = setInterval(verifyHealth, 30000)
    return () => clearInterval(interval)
  }, [verifyHealth])

  return (
    <header className="app-header">
      <div className="header-brand">
        <Link to="/" className="brand-logo-link">
          <div className="brand-icon">📣</div>
          <div className="brand-text">
            <span className="brand-title">PR Campaign Assistant</span>
            <span className="brand-badge">MVP</span>
          </div>
        </Link>
      </div>

      <div className="header-actions">
        <div
          className={`backend-status-badge status-${backendStatus}`}
          title={`Backend status: ${backendStatus}`}
        >
          <span className="status-indicator-dot" />
          <span className="status-indicator-text">
            {backendStatus === 'checking' && 'Checking API...'}
            {backendStatus === 'online' && 'API Connected'}
            {backendStatus === 'offline' && 'API Offline'}
          </span>
        </div>
      </div>
    </header>
  )
}
