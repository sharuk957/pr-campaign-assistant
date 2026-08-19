import type { FC } from 'react'

interface ErrorAlertProps {
  title?: string
  message: string
  code?: string
  onRetry?: () => void
  onDismiss?: () => void
}

export const ErrorAlert: FC<ErrorAlertProps> = ({
  title = 'Something went wrong',
  message,
  code,
  onRetry,
  onDismiss,
}) => {
  return (
    <div className="error-alert" role="alert">
      <div className="error-alert-header">
        <span className="error-alert-icon" aria-hidden="true">⚠️</span>
        <strong className="error-alert-title">{title}</strong>
        {code && <span className="error-alert-code">[{code}]</span>}
        {onDismiss && (
          <button
            type="button"
            className="error-alert-dismiss"
            onClick={onDismiss}
            aria-label="Dismiss error"
          >
            ✕
          </button>
        )}
      </div>
      <div className="error-alert-body">
        <p>{message}</p>
      </div>
      {onRetry && (
        <div className="error-alert-actions">
          <button type="button" className="btn btn-secondary btn-sm" onClick={onRetry}>
            Try again
          </button>
        </div>
      )}
    </div>
  )
}
