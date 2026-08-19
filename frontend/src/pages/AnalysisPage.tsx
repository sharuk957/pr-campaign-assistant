import { useCallback, useEffect, useState, type FC } from 'react'
import { Link, useNavigate } from '../router'
import { getCampaign, listAnalyses, listJournalists, runCampaignAnalysis } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorAlert } from '../components/common/ErrorAlert'
import type { Analysis, AsyncState, Journalist } from '../types'

interface AnalysisRow {
  journalistId: string
  name: string
  publication: string
  status: 'success' | 'failed' | 'pending'
  analysis: Analysis | null
  error: string | null
}

function statusRank(row: AnalysisRow): number {
  if (row.status === 'success') return 0
  if (row.status === 'pending') return 1
  return 2
}

function sortRows(rows: AnalysisRow[]): AnalysisRow[] {
  return [...rows].sort((a, b) => {
    const rankDiff = statusRank(a) - statusRank(b)
    if (rankDiff !== 0) return rankDiff
    if (a.status === 'success' && b.status === 'success') {
      return (b.analysis?.score ?? 0) - (a.analysis?.score ?? 0)
    }
    return 0
  })
}

function buildRows(journalists: Journalist[], analyses: Analysis[]): AnalysisRow[] {
  const analysisByJournalistId = new Map(analyses.map((a) => [a.journalist_id, a]))
  return journalists.map((journalist) => {
    const analysis = analysisByJournalistId.get(journalist.id) ?? null
    return {
      journalistId: journalist.id,
      name: journalist.name,
      publication: journalist.publication,
      status: analysis ? 'success' : 'pending',
      analysis,
      error: null,
    }
  })
}

export const AnalysisPage: FC = () => {
  const navigate = useNavigate()

  const [campaignId, setCampaignId] = useState<string | null>(null)
  const [checkingCampaign, setCheckingCampaign] = useState(
    () => localStorage.getItem('active_campaign_id') !== null
  )

  const [dataState, setDataState] = useState<AsyncState<AnalysisRow[]>>({
    status: 'idle',
    data: null,
    error: null,
  })

  const [isRunning, setIsRunning] = useState(false)
  const [runError, setRunError] = useState<string | null>(null)
  const [runSummary, setRunSummary] = useState<{ succeeded: number; failed: number } | null>(null)

  const loadData = useCallback((activeCampaignId: string) => {
    setDataState({ status: 'loading', data: null, error: null })
    Promise.all([listJournalists(activeCampaignId), listAnalyses(activeCampaignId)])
      .then(([journalists, analyses]) => {
        setDataState({ status: 'success', data: buildRows(journalists, analyses), error: null })
      })
      .catch((err) => {
        setDataState({
          status: 'error',
          data: null,
          error: err instanceof Error ? err.message : 'Failed to load analysis data',
        })
      })
  }, [])

  useEffect(() => {
    const activeId = localStorage.getItem('active_campaign_id')
    if (!activeId) return

    getCampaign(activeId)
      .then((campaign) => {
        setCampaignId(campaign.id)
        loadData(campaign.id)
      })
      .catch(() => setCampaignId(null))
      .finally(() => setCheckingCampaign(false))
  }, [loadData])

  const handleRunAnalysis = async () => {
    if (!campaignId) return

    setIsRunning(true)
    setRunError(null)
    setRunSummary(null)

    try {
      const runResult = await runCampaignAnalysis(campaignId)
      setRunSummary({ succeeded: runResult.succeeded, failed: runResult.failed })

      setDataState((prev) => {
        const previousRows = prev.data ?? []
        const rowsByJournalistId = new Map(previousRows.map((row) => [row.journalistId, row]))

        for (const outcome of runResult.results) {
          rowsByJournalistId.set(outcome.journalist_id, {
            journalistId: outcome.journalist_id,
            name: outcome.journalist_name,
            publication: rowsByJournalistId.get(outcome.journalist_id)?.publication ?? '',
            status: outcome.status,
            analysis: outcome.analysis,
            error: outcome.error,
          })
        }

        return {
          status: 'success',
          data: sortRows(Array.from(rowsByJournalistId.values())),
          error: null,
        }
      })
    } catch (err) {
      setRunError(err instanceof Error ? err.message : 'Failed to run journalist analysis')
    } finally {
      setIsRunning(false)
    }
  }

  if (checkingCampaign) {
    return (
      <div className="page analysis-page">
        <LoadingSpinner message="Loading campaign data..." />
      </div>
    )
  }

  if (!campaignId) {
    return (
      <div className="page analysis-page">
        <div className="page-header">
          <div className="page-header-text">
            <span className="page-step-indicator">Step 3 of 5</span>
            <h1 className="page-title">Relevance Analysis & Rankings</h1>
            <p className="page-description">
              AI-driven relevance scores, priority rankings, and supporting evidence matching journalists to
              campaign themes.
            </p>
          </div>
        </div>

        <div className="page-card empty-state-card">
          <div className="placeholder-icon">📋</div>
          <h2 className="placeholder-title">No Active Campaign</h2>
          <p className="placeholder-text">Create a campaign first to analyze journalists.</p>
          <div className="placeholder-actions">
            <Link to="/" className="btn btn-primary">
              &larr; Go to Campaign Setup
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const rows = dataState.data ?? []

  return (
    <div className="page analysis-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 3 of 5</span>
          <h1 className="page-title">Relevance Analysis & Rankings</h1>
          <p className="page-description">
            AI-driven relevance scores, priority rankings, and supporting evidence matching journalists to
            campaign themes.
          </p>
        </div>
      </div>

      <div className="page-card analysis-run-card">
        <div className="card-header-row">
          <h2 className="form-title">Run Relevance Analysis</h2>
          <button
            type="button"
            className="btn btn-primary"
            disabled={isRunning || dataState.status !== 'success' || rows.length === 0}
            onClick={handleRunAnalysis}
          >
            {isRunning ? (
              <LoadingSpinner inline message="Analyzing journalists..." size="small" />
            ) : rows.some((r) => r.status !== 'pending') ? (
              'Re-run Analysis'
            ) : (
              'Run Analysis'
            )}
          </button>
        </div>
        <p className="form-hint">
          Evaluates every journalist in this campaign against your campaign details using AI.
        </p>

        {runError && (
          <ErrorAlert title="Analysis Failed" message={runError} onDismiss={() => setRunError(null)} />
        )}

        {runSummary && (
          <div className="import-summary" role="status">
            <span className="import-success-badge">
              ✓ {runSummary.succeeded} analyzed
              {runSummary.failed > 0 ? ` · ${runSummary.failed} failed` : ''}
            </span>
          </div>
        )}
      </div>

      {dataState.status === 'loading' && (
        <div className="page-card">
          <LoadingSpinner message="Loading journalists and analysis results..." />
        </div>
      )}

      {dataState.status === 'error' && (
        <div className="page-card">
          <ErrorAlert
            title="Unable to Load Analysis Data"
            message={dataState.error ?? 'Something went wrong'}
            onRetry={() => loadData(campaignId)}
          />
        </div>
      )}

      {dataState.status === 'success' && rows.length === 0 && (
        <div className="page-card empty-state-card">
          <div className="placeholder-icon">👥</div>
          <h2 className="placeholder-title">No Journalists to Analyze</h2>
          <p className="placeholder-text">Import journalists first before running relevance analysis.</p>
          <div className="placeholder-actions">
            <Link to="/journalists" className="btn btn-primary">
              &larr; Import Journalists
            </Link>
          </div>
        </div>
      )}

      {dataState.status === 'success' && rows.length > 0 && (
        <div className="page-card">
          {rows.every((row) => row.status === 'pending') && (
            <p className="placeholder-text analysis-pending-hint">
              These journalists have not been analyzed yet. Click "Run Analysis" above to get started.
            </p>
          )}

          {rows.map((row) => (
            <div key={row.journalistId} className="preview-ranking-item">
              {row.status === 'success' && row.analysis && (
                <span className={`ranking-badge ${row.analysis.priority}`}>
                  {row.analysis.score} / 100 &bull; {row.analysis.priority} priority
                </span>
              )}
              {row.status === 'pending' && <span className="ranking-badge pending">Not analyzed</span>}
              {row.status === 'failed' && <span className="ranking-badge failed">Analysis failed</span>}

              <div className="ranking-info">
                <strong>
                  {row.name} &mdash; {row.publication}
                </strong>
                {row.status === 'success' && row.analysis && (
                  <p>{row.analysis.reasons[0] ?? 'No summary reason provided.'}</p>
                )}
                {row.status === 'pending' && <p>Waiting to be analyzed.</p>}
                {row.status === 'failed' && <p>{row.error ?? 'The AI provider could not be reached.'}</p>}
              </div>

              <button
                type="button"
                className="btn btn-sm btn-secondary"
                onClick={() => navigate(`/journalists/${row.journalistId}`)}
              >
                View Details &rarr;
              </button>
            </div>
          ))}
        </div>
      )}

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
