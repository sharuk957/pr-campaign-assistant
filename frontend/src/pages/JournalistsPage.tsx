import { useCallback, useEffect, useRef, useState, type ChangeEvent, type FC } from 'react'
import { Link, useNavigate } from '../router'
import { getCampaign, importJournalistsCsv, listJournalists } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorAlert } from '../components/common/ErrorAlert'
import type { AsyncState, Journalist, JournalistImportResult } from '../types'

function splitTags(value: string): string[] {
  return value
    .split(/[;,]/)
    .map((t) => t.trim())
    .filter(Boolean)
}

export const JournalistsPage: FC = () => {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [campaignId, setCampaignId] = useState<string | null>(null)
  const [campaignName, setCampaignName] = useState<string | null>(null)
  const [checkingCampaign, setCheckingCampaign] = useState(
    () => localStorage.getItem('active_campaign_id') !== null
  )

  const [journalistsState, setJournalistsState] = useState<AsyncState<Journalist[]>>({
    status: 'idle',
    data: null,
    error: null,
  })

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [importResult, setImportResult] = useState<JournalistImportResult | null>(null)

  const loadJournalists = useCallback((activeCampaignId: string) => {
    setJournalistsState({ status: 'loading', data: null, error: null })
    listJournalists(activeCampaignId)
      .then((journalists) => {
        setJournalistsState({ status: 'success', data: journalists, error: null })
      })
      .catch((err) => {
        setJournalistsState({
          status: 'error',
          data: null,
          error: err instanceof Error ? err.message : 'Failed to load journalists',
        })
      })
  }, [])

  useEffect(() => {
    const activeId = localStorage.getItem('active_campaign_id')
    if (!activeId) return

    getCampaign(activeId)
      .then((campaign) => {
        setCampaignId(campaign.id)
        setCampaignName(campaign.name)
        loadJournalists(campaign.id)
      })
      .catch(() => {
        setCampaignId(null)
      })
      .finally(() => setCheckingCampaign(false))
  }, [loadJournalists])

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null
    setSelectedFile(file)
    setUploadError(null)
    setImportResult(null)
  }

  const handleUpload = async () => {
    if (!campaignId || !selectedFile) return

    setIsUploading(true)
    setUploadError(null)
    setImportResult(null)

    try {
      const result = await importJournalistsCsv(campaignId, selectedFile)
      setImportResult(result)
      setSelectedFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      loadJournalists(campaignId)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Failed to import journalists')
    } finally {
      setIsUploading(false)
    }
  }

  if (checkingCampaign) {
    return (
      <div className="page journalists-page">
        <LoadingSpinner message="Loading campaign data..." />
      </div>
    )
  }

  if (!campaignId) {
    return (
      <div className="page journalists-page">
        <div className="page-header">
          <div className="page-header-text">
            <span className="page-step-indicator">Step 2 of 5</span>
            <h1 className="page-title">Journalist Management</h1>
            <p className="page-description">
              Upload your CSV journalist roster or view existing media contacts associated with this campaign.
            </p>
          </div>
        </div>

        <div className="page-card empty-state-card">
          <div className="placeholder-icon">📋</div>
          <h2 className="placeholder-title">No Active Campaign</h2>
          <p className="placeholder-text">
            Create a campaign first so imported journalists can be associated with it.
          </p>
          <div className="placeholder-actions">
            <Link to="/" className="btn btn-primary">
              &larr; Go to Campaign Setup
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const journalists = journalistsState.data ?? []

  return (
    <div className="page journalists-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 2 of 5</span>
          <h1 className="page-title">Journalist Management</h1>
          <p className="page-description">
            Upload your CSV journalist roster for <strong>{campaignName}</strong> or review existing media
            contacts associated with this campaign.
          </p>
        </div>
      </div>

      <div className="page-card upload-card">
        <h2 className="form-title">Import Journalists from CSV</h2>
        <p className="form-hint upload-hint">
          Required columns: name, email, publication, role, topics, bio, recent_articles
        </p>

        <div className="upload-controls-row">
          <input
            ref={fileInputRef}
            id="journalist-csv-input"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="file-input-hidden"
          />
          <label htmlFor="journalist-csv-input" className="btn btn-secondary">
            Choose CSV File
          </label>
          <span className="selected-file-name">
            {selectedFile ? selectedFile.name : 'No file selected'}
          </span>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!selectedFile || isUploading}
            onClick={handleUpload}
          >
            {isUploading ? <LoadingSpinner inline message="Importing..." size="small" /> : 'Import Journalists'}
          </button>
        </div>

        {uploadError && (
          <ErrorAlert title="Import Failed" message={uploadError} onDismiss={() => setUploadError(null)} />
        )}

        {importResult && (
          <div className="import-summary" role="status">
            <div className="import-summary-headline">
              <span className="import-success-badge">
                ✓ {importResult.imported_count} of {importResult.total_rows} journalist
                {importResult.total_rows === 1 ? '' : 's'} imported
              </span>
            </div>

            {importResult.errors.length > 0 && (
              <div className="import-errors-list">
                <p className="import-errors-title">
                  {importResult.errors.length} row{importResult.errors.length === 1 ? '' : 's'} could not be imported:
                </p>
                <ul>
                  {importResult.errors.map((error) => (
                    <li key={error.row}>
                      Row {error.row}: {error.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="page-card journalist-list-card">
        <h2 className="form-title">Campaign Journalists</h2>

        {journalistsState.status === 'loading' && <LoadingSpinner message="Loading journalists..." />}

        {journalistsState.status === 'error' && (
          <ErrorAlert
            title="Unable to Load Journalists"
            message={journalistsState.error ?? 'Something went wrong'}
            onRetry={() => loadJournalists(campaignId)}
          />
        )}

        {journalistsState.status === 'success' && journalists.length === 0 && (
          <div className="empty-state">
            <div className="placeholder-icon">👥</div>
            <p className="placeholder-text">
              No journalists yet. Import a CSV file above to build your media roster.
            </p>
          </div>
        )}

        {journalistsState.status === 'success' && journalists.length > 0 && (
          <div className="journalist-table-wrapper">
            <table className="journalist-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Publication</th>
                  <th>Role</th>
                  <th>Topics</th>
                </tr>
              </thead>
              <tbody>
                {journalists.map((journalist) => (
                  <tr
                    key={journalist.id}
                    className="journalist-table-row"
                    onClick={() => navigate(`/journalists/${journalist.id}`)}
                  >
                    <td>
                      <strong>{journalist.name}</strong>
                    </td>
                    <td>{journalist.publication}</td>
                    <td>{journalist.role}</td>
                    <td>
                      <span className="preview-tags">
                        {splitTags(journalist.topics).map((topic) => (
                          <span key={topic} className="tag">
                            {topic}
                          </span>
                        ))}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="placeholder-actions">
        <Link to="/" className="btn btn-secondary">
          &larr; Back to Campaign
        </Link>
        <Link to="/analysis" className="btn btn-primary">
          Next: Run AI Relevance Analysis &rarr;
        </Link>
      </div>
    </div>
  )
}
