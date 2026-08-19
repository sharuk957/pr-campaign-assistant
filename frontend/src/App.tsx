import { useEffect, useState } from 'react'
import { checkBackendHealth } from './services/api'
import './App.css'

function App() {
  const [backendStatus, setBackendStatus] = useState<'loading' | 'connected' | 'error'>(
    'loading',
  )
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    checkBackendHealth()
      .then(() => setBackendStatus('connected'))
      .catch((error: Error) => {
        setBackendStatus('error')
        setErrorMessage(error.message)
      })
  }, [])

  return (
    <main className="app">
      <h1>PR Campaign Assistant</h1>
      <p>Identify relevant journalists and generate personalized outreach pitches.</p>

      <section className="status-card">
        <h2>Backend connection</h2>
        {backendStatus === 'loading' && <p>Checking backend health...</p>}
        {backendStatus === 'connected' && (
          <p className="status-ok">Connected — backend health check passed.</p>
        )}
        {backendStatus === 'error' && (
          <p className="status-error">
            Unable to reach the backend.
            {errorMessage ? ` ${errorMessage}` : ''}
          </p>
        )}
      </section>
    </main>
  )
}

export default App
