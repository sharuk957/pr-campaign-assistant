import { useEffect, useState, type FC } from 'react'
import { Link, useParams } from '../router'
import {
  ApiRequestError,
  generatePitch,
  getJournalist,
  getPitchForJournalist,
} from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorAlert } from '../components/common/ErrorAlert'
import type { AsyncState, Journalist, Pitch } from '../types'

type PitchLoadStatus = 'idle' | 'loading' | 'success' | 'not-generated' | 'error'

export const PitchPage: FC = () => {
  const { id: journalistId } = useParams()
  const [campaignId] = useState<string | null>(() => localStorage.getItem('active_campaign_id'))

  const [journalistState, setJournalistState] = useState<AsyncState<Journalist>>({
    status: 'idle',
    data: null,
    error: null,
  })

  const [pitchState, setPitchState] = useState<{
    status: PitchLoadStatus
    data: Pitch | null
    error: string | null
  }>({ status: 'idle', data: null, error: null })

  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [needsAnalysis, setNeedsAnalysis] = useState(false)
  const [copied, setCopied] = useState(false)

  const loadJournalist = () => {
    if (!campaignId || !journalistId) return
    setJournalistState({ status: 'loading', data: null, error: null })
    getJournalist(campaignId, journalistId)
      .then((journalist) => setJournalistState({ status: 'success', data: journalist, error: null }))
      .catch((err) =>
        setJournalistState({
          status: 'error',
          data: null,
          error: err instanceof Error ? err.message : 'Failed to load journalist',
        })
      )
  }

  const loadPitch = () => {
    if (!campaignId || !journalistId) return
    setPitchState({ status: 'loading', data: null, error: null })
    getPitchForJournalist(campaignId, journalistId)
      .then((pitch) => setPitchState({ status: 'success', data: pitch, error: null }))
      .catch((err) => {
        if (err instanceof ApiRequestError && err.status === 404) {
          setPitchState({ status: 'not-generated', data: null, error: null })
          return
        }
        setPitchState({
          status: 'error',
          data: null,
          error: err instanceof Error ? err.message : 'Failed to load pitch',
        })
      })
  }

  useEffect(() => {
    loadJournalist()
    loadPitch()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [campaignId, journalistId])

  const handleGenerate = async () => {
    if (!campaignId || !journalistId) return

    setIsGenerating(true)
    setGenerateError(null)
    setNeedsAnalysis(false)
    setCopied(false)

    try {
      const pitch = await generatePitch(campaignId, journalistId)
      setPitchState({ status: 'success', data: pitch, error: null })
    } catch (err) {
      if (err instanceof ApiRequestError && err.code === 'BAD_REQUEST') {
        setNeedsAnalysis(true)
      }
      setGenerateError(err instanceof Error ? err.message : 'Failed to generate pitch')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopy = async () => {
    if (!pitchState.data) return
    const text = `Subject: ${pitchState.data.subject}\n\n${pitchState.data.body}`
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setGenerateError('Unable to copy to clipboard. Please copy the text manually.')
    }
  }

  if (!campaignId) {
    return (
      <div className="page pitch-page">
        <PageHeader />
        <div className="page-card empty-state-card">
          <div className="placeholder-icon">📋</div>
          <h2 className="placeholder-title">No Active Campaign</h2>
          <p className="placeholder-text">Create a campaign first to generate outreach pitches.</p>
          <div className="placeholder-actions">
            <Link to="/" className="btn btn-primary">
              &larr; Go to Campaign Setup
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!journalistId) {
    return (
      <div className="page pitch-page">
        <PageHeader />
        <div className="page-card empty-state-card">
          <div className="placeholder-icon">✉️</div>
          <h2 className="placeholder-title">No Journalist Selected</h2>
          <p className="placeholder-text">
            Choose a journalist from the roster to generate a personalized pitch.
          </p>
          <div className="placeholder-actions">
            <Link to="/journalists" className="btn btn-primary">
              &larr; Back to Journalists
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const journalist = journalistState.data
  const hasPitch = pitchState.status === 'success' && pitchState.data

  return (
    <div className="page pitch-page">
      <PageHeader />

      <div className="page-card">
        {journalistState.status === 'loading' && (
          <LoadingSpinner message="Loading journalist..." size="small" />
        )}
        {journalistState.status === 'error' && (
          <ErrorAlert
            title="Unable to Load Journalist"
            message={journalistState.error ?? 'Something went wrong'}
            onRetry={loadJournalist}
          />
        )}
        {journalist && (
          <div className="card-header-row">
            <div>
              <h2 className="form-title">
                Pitch for {journalist.name} &mdash; {journalist.publication}
              </h2>
              <p className="form-hint">
                Generated using this campaign, {journalist.name}'s profile, and their relevance
                analysis.
              </p>
            </div>
            <button
              type="button"
              className="btn btn-primary"
              disabled={isGenerating}
              onClick={handleGenerate}
            >
              {isGenerating ? (
                <LoadingSpinner inline message="Generating..." size="small" />
              ) : hasPitch ? (
                'Regenerate Pitch'
              ) : (
                'Generate Pitch'
              )}
            </button>
          </div>
        )}

        {generateError && (
          <ErrorAlert
            title="Pitch Generation Failed"
            message={generateError}
            onDismiss={() => {
              setGenerateError(null)
              setNeedsAnalysis(false)
            }}
            onRetry={needsAnalysis ? undefined : handleGenerate}
          />
        )}
        {needsAnalysis && (
          <p className="detail-text">
            This journalist needs a relevance analysis first. Run it from the{' '}
            <Link to={`/journalists/${journalistId}`}>journalist details page</Link> or the{' '}
            <Link to="/analysis">Analysis page</Link>, then try again.
          </p>
        )}

        {pitchState.status === 'loading' && <LoadingSpinner message="Loading pitch..." />}

        {pitchState.status === 'error' && (
          <ErrorAlert
            title="Unable to Load Pitch"
            message={pitchState.error ?? 'Something went wrong'}
            onRetry={loadPitch}
          />
        )}

        {pitchState.status === 'not-generated' && !generateError && (
          <div className="empty-state">
            <div className="placeholder-icon">✉️</div>
            <p className="placeholder-text">
              No pitch has been generated yet. Click "Generate Pitch" above to create one.
            </p>
          </div>
        )}

        {hasPitch && pitchState.data && (
          <div className="pitch-preview-box">
            <div className="pitch-subject">
              <strong>Subject:</strong> {pitchState.data.subject}
            </div>
            <div className="pitch-body">
              {pitchState.data.body.split(/\n+/).map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
            <div className="pitch-actions-row">
              <button type="button" className="btn btn-secondary" onClick={handleCopy}>
                {copied ? '✓ Copied!' : 'Copy Pitch'}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="placeholder-actions">
        <Link to={`/journalists/${journalistId}`} className="btn btn-secondary">
          &larr; Back to Journalist Details
        </Link>
        <Link
          to="/"
          className="btn btn-primary"
          onClick={() => localStorage.removeItem('active_campaign_id')}
        >
          Start New Campaign
        </Link>
      </div>
    </div>
  )
}

const PageHeader: FC = () => (
  <div className="page-header">
    <div className="page-header-text">
      <span className="page-step-indicator">Step 5 of 5</span>
      <h1 className="page-title">Personalized Pitch Outreach</h1>
      <p className="page-description">
        Review, regenerate, and copy custom outreach pitches tailored to individual journalists and
        grounded in campaign themes.
      </p>
    </div>
  </div>
)
