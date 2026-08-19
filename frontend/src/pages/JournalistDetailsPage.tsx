import { useEffect, useState, type FC } from 'react'
import { Link, useParams } from '../router'
import { ApiRequestError, getAnalysisForJournalist, getJournalist } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorAlert } from '../components/common/ErrorAlert'
import type { Analysis, AsyncState, Journalist } from '../types'

function splitList(value: string): string[] {
  return value
    .split(/[;,]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

export const JournalistDetailsPage: FC = () => {
  const { id } = useParams()
  const [campaignId] = useState<string | null>(() => localStorage.getItem('active_campaign_id'))
  const [state, setState] = useState<AsyncState<Journalist>>({ status: 'idle', data: null, error: null })

  type AnalysisLoadStatus = 'idle' | 'loading' | 'success' | 'not-analyzed' | 'error'
  const [analysisState, setAnalysisState] = useState<{
    status: AnalysisLoadStatus
    data: Analysis | null
    error: string | null
  }>({ status: 'idle', data: null, error: null })

  const loadJournalist = () => {
    if (!campaignId || !id) return
    setState({ status: 'loading', data: null, error: null })
    getJournalist(campaignId, id)
      .then((journalist) => setState({ status: 'success', data: journalist, error: null }))
      .catch((err) =>
        setState({
          status: 'error',
          data: null,
          error: err instanceof Error ? err.message : 'Failed to load journalist',
        })
      )
  }

  const loadAnalysis = () => {
    if (!campaignId || !id) return
    setAnalysisState({ status: 'loading', data: null, error: null })
    getAnalysisForJournalist(campaignId, id)
      .then((analysis) => setAnalysisState({ status: 'success', data: analysis, error: null }))
      .catch((err) => {
        if (err instanceof ApiRequestError && err.status === 404) {
          setAnalysisState({ status: 'not-analyzed', data: null, error: null })
          return
        }
        setAnalysisState({
          status: 'error',
          data: null,
          error: err instanceof Error ? err.message : 'Failed to load analysis',
        })
      })
  }

  useEffect(() => {
    loadJournalist()
    loadAnalysis()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignId, id])

  const renderBody = () => {
    if (!campaignId) {
      return (
        <div className="page-card empty-state-card">
          <div className="placeholder-icon">📋</div>
          <h2 className="placeholder-title">No Active Campaign</h2>
          <p className="placeholder-text">Create a campaign first to view journalist details.</p>
          <div className="placeholder-actions">
            <Link to="/" className="btn btn-primary">
              &larr; Go to Campaign Setup
            </Link>
          </div>
        </div>
      )
    }

    if (!id) {
      return (
        <div className="page-card empty-state-card">
          <div className="placeholder-icon">🔍</div>
          <h2 className="placeholder-title">No Journalist Selected</h2>
          <p className="placeholder-text">Choose a journalist from the roster to view their profile.</p>
          <div className="placeholder-actions">
            <Link to="/journalists" className="btn btn-primary">
              &larr; Back to Journalists
            </Link>
          </div>
        </div>
      )
    }

    if (state.status === 'loading' || state.status === 'idle') {
      return (
        <div className="page-card">
          <LoadingSpinner message="Loading journalist profile..." />
        </div>
      )
    }

    if (state.status === 'error') {
      return (
        <div className="page-card">
          <ErrorAlert
            title="Unable to Load Journalist"
            message={state.error ?? 'Something went wrong'}
            onRetry={loadJournalist}
          />
        </div>
      )
    }

    const journalist = state.data as Journalist
    const topics = splitList(journalist.topics)
    const recentArticles = splitList(journalist.recent_articles)

    return (
      <div className="page-card">
        <div className="detail-split">
          <div className="detail-pane">
            <h3>Source Information</h3>
            <p>
              <strong>Name:</strong> {journalist.name}
            </p>
            <p>
              <strong>Email:</strong> {journalist.email}
            </p>
            <p>
              <strong>Publication:</strong> {journalist.publication}
            </p>
            <p>
              <strong>Role:</strong> {journalist.role}
            </p>
            <p>
              <strong>Topics:</strong>
            </p>
            <div className="topic-tags-container">
              {topics.length > 0 ? (
                topics.map((topic) => (
                  <span key={topic} className="tag topic-tag">
                    {topic}
                  </span>
                ))
              ) : (
                <span className="detail-text">No topics recorded</span>
              )}
            </div>
            <p>
              <strong>Biography:</strong>
            </p>
            <p className="detail-text">{journalist.bio || 'No biography available'}</p>
            <p>
              <strong>Recent Articles:</strong>
            </p>
            {recentArticles.length > 0 ? (
              <ul>
                {recentArticles.map((article) => (
                  <li key={article}>{article}</li>
                ))}
              </ul>
            ) : (
              <p className="detail-text">No recent articles recorded</p>
            )}
          </div>

          <div className="detail-pane ai-pane">
            <h3>AI Relevance Breakdown</h3>

            {analysisState.status === 'loading' && <LoadingSpinner message="Loading analysis..." size="small" />}

            {analysisState.status === 'error' && (
              <ErrorAlert
                title="Unable to Load Analysis"
                message={analysisState.error ?? 'Something went wrong'}
                onRetry={loadAnalysis}
              />
            )}

            {analysisState.status === 'not-analyzed' && (
              <p className="detail-text">
                This journalist has not been analyzed yet. Run relevance analysis from the{' '}
                <Link to="/analysis">Analysis page</Link> to see a score, priority, and supporting
                evidence here.
              </p>
            )}

            {analysisState.status === 'success' && analysisState.data && (
              <>
                <p>
                  <strong>Score:</strong> {analysisState.data.score} / 100 (
                  <span className={`priority-text ${analysisState.data.priority}`}>
                    {analysisState.data.priority} priority
                  </span>
                  )
                </p>

                <p>
                  <strong>Reasons:</strong>
                </p>
                {analysisState.data.reasons.length > 0 ? (
                  <ul>
                    {analysisState.data.reasons.map((reason) => (
                      <li key={reason}>{reason}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="detail-text">No reasons provided</p>
                )}

                <p>
                  <strong>Supporting Evidence:</strong>
                </p>
                {analysisState.data.supporting_evidence.length > 0 ? (
                  <ul>
                    {analysisState.data.supporting_evidence.map((evidence) => (
                      <li key={evidence}>{evidence}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="detail-text">No supporting evidence provided</p>
                )}

                <p>
                  <strong>Potential Concerns:</strong>
                </p>
                {analysisState.data.concerns.length > 0 ? (
                  <ul>
                    {analysisState.data.concerns.map((concern) => (
                      <li key={concern}>{concern}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="detail-text">No concerns noted</p>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    )
  }

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

      {renderBody()}

      <div className="placeholder-actions">
        <Link to="/journalists" className="btn btn-secondary">
          &larr; Back to Journalists
        </Link>
        <Link to="/pitch" className="btn btn-primary">
          Next: Generate Outreach Pitch &rarr;
        </Link>
      </div>
    </div>
  )
}
