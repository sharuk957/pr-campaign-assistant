import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  private handleReload = () => {
    window.location.reload()
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-fallback">
          <div className="error-boundary-card">
            <h2>Application Error</h2>
            <p>
              Something went wrong loading this page. This has been noted &mdash; try again or reload
              the page.
            </p>
            {this.state.error?.message && (
              <details className="error-boundary-details">
                <summary>Technical details</summary>
                <p className="error-boundary-message">{this.state.error.message}</p>
              </details>
            )}
            <div className="error-boundary-buttons">
              <button type="button" className="btn btn-primary" onClick={this.handleReset}>
                Try again
              </button>
              <button type="button" className="btn btn-secondary" onClick={this.handleReload}>
                Reload page
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
