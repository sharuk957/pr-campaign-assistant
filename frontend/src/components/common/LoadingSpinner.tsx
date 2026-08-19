import type { FC } from 'react'

interface LoadingSpinnerProps {
  message?: string
  size?: 'small' | 'medium' | 'large'
  inline?: boolean
}

export const LoadingSpinner: FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 'medium',
  inline = false,
}) => {
  if (inline) {
    return (
      <span className={`loading-inline loading-${size}`} role="status" aria-live="polite">
        <span className="spinner-icon" />
        {message && <span className="spinner-message">{message}</span>}
      </span>
    )
  }

  return (
    <div className={`loading-container loading-${size}`} role="status" aria-live="polite">
      <div className="spinner-icon" />
      {message && <p className="spinner-message">{message}</p>}
    </div>
  )
}
