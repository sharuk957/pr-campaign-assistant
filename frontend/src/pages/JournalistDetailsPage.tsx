import { useEffect, useState, type FC } from 'react'
import { Link, useParams } from '../router'
import { getJournalist } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorAlert } from '../components/common/ErrorAlert'
import type { AsyncState, Journalist } from '../types'

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

  useEffect(() => {
    loadJournalist()
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
            <p className="detail-text">
              AI-generated relevance analysis will appear here once journalist analysis has been run.
            </p>
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
