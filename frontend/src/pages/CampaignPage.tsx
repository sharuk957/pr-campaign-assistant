import { useEffect, useState, type FC, type FormEvent } from 'react'
import { useNavigate } from '../router'
import { createCampaign, getCampaign, listCampaigns } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ErrorAlert } from '../components/common/ErrorAlert'
import type { Campaign, CampaignCreatePayload } from '../types'

const SAMPLE_CAMPAIGN: CampaignCreatePayload = {
  name: 'AI Developer Security Platform Launch',
  company_name: 'Acme Security',
  product_description:
    'An AI-powered platform that detects security vulnerabilities and secret leaks in Python applications during code review.',
  campaign_description:
    'Acme has launched a next-generation AI security assistant that automatically flags vulnerabilities in Python code and suggests automated fixes.',
  target_audience: 'Software engineers, DevOps leads, engineering managers, and Python developers',
  key_topics: 'AI; Cybersecurity; Python; Developer Tools; Application Security',
  desired_outcome:
    'Generate media coverage among major technology publications and developer newsletters.',
}

interface FormErrors {
  name?: string
  company_name?: string
  product_description?: string
  campaign_description?: string
  target_audience?: string
  key_topics?: string
  desired_outcome?: string
}

export const CampaignPage: FC = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<CampaignCreatePayload>({
    name: '',
    company_name: '',
    product_description: '',
    campaign_description: '',
    target_audience: '',
    key_topics: '',
    desired_outcome: '',
  })

  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [activeCampaign, setActiveCampaign] = useState<Campaign | null>(null)
  const [isLoadingActive, setIsLoadingActive] = useState(true)
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    const activeId = localStorage.getItem('active_campaign_id')
    if (activeId) {
      getCampaign(activeId)
        .then((campaign) => {
          setActiveCampaign(campaign)
          setShowForm(false)
        })
        .catch(() => {
          // If active ID is invalid, check if any campaigns exist
          listCampaigns()
            .then((campaigns) => {
              if (campaigns.length > 0) {
                setActiveCampaign(campaigns[0])
                localStorage.setItem('active_campaign_id', campaigns[0].id)
                setShowForm(false)
              } else {
                setShowForm(true)
              }
            })
            .catch(() => setShowForm(true))
        })
        .finally(() => setIsLoadingActive(false))
    } else {
      listCampaigns()
        .then((campaigns) => {
          if (campaigns.length > 0) {
            setActiveCampaign(campaigns[0])
            localStorage.setItem('active_campaign_id', campaigns[0].id)
            setShowForm(false)
          } else {
            setShowForm(true)
          }
        })
        .catch(() => setShowForm(true))
        .finally(() => setIsLoadingActive(false))
    }
  }, [])

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}
    if (!formData.name.trim()) newErrors.name = 'Campaign name is required'
    if (!formData.company_name.trim()) newErrors.company_name = 'Company name is required'
    if (!formData.product_description.trim())
      newErrors.product_description = 'Product description is required'
    if (!formData.campaign_description.trim())
      newErrors.campaign_description = 'Campaign description is required'
    if (!formData.target_audience.trim())
      newErrors.target_audience = 'Target audience is required'
    if (!formData.key_topics.trim()) newErrors.key_topics = 'Key topics are required'
    if (!formData.desired_outcome.trim())
      newErrors.desired_outcome = 'Desired outcome is required'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (field: keyof CampaignCreatePayload, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  const handleFillSample = () => {
    setFormData(SAMPLE_CAMPAIGN)
    setErrors({})
    setApiError(null)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setApiError(null)

    if (!validateForm()) return

    setIsSubmitting(true)
    try {
      const created = await createCampaign(formData)
      setActiveCampaign(created)
      localStorage.setItem('active_campaign_id', created.id)
      setShowForm(false)
    } catch (err) {
      setApiError(err instanceof Error ? err.message : 'Failed to create campaign')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleStartNew = () => {
    setFormData({
      name: '',
      company_name: '',
      product_description: '',
      campaign_description: '',
      target_audience: '',
      key_topics: '',
      desired_outcome: '',
    })
    setErrors({})
    setApiError(null)
    setShowForm(true)
  }

  if (isLoadingActive) {
    return (
      <div className="page campaign-page">
        <LoadingSpinner message="Loading campaign data..." />
      </div>
    )
  }

  return (
    <div className="page campaign-page">
      <div className="page-header">
        <div className="page-header-text">
          <span className="page-step-indicator">Step 1 of 5</span>
          <h1 className="page-title">Campaign Management</h1>
          <p className="page-description">
            Define your campaign context, company profile, target audience, and key topics to anchor AI journalist matching and personalized pitch generation.
          </p>
        </div>
      </div>

      {apiError && (
        <ErrorAlert
          title="Campaign Error"
          message={apiError}
          onDismiss={() => setApiError(null)}
        />
      )}

      {activeCampaign && !showForm ? (
        <div className="page-card campaign-active-card">
          <div className="card-header-row">
            <div className="active-badge-tag">
              <span className="active-dot" /> Active Campaign
            </div>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleStartNew}
            >
              + Create New Campaign
            </button>
          </div>

          <h2 className="active-campaign-title">{activeCampaign.name}</h2>
          <span className="active-company-name">{activeCampaign.company_name}</span>

          <div className="campaign-details-grid">
            <div className="detail-item full-width">
              <span className="detail-label">Product / Service</span>
              <p className="detail-text">{activeCampaign.product_description}</p>
            </div>

            <div className="detail-item full-width">
              <span className="detail-label">Campaign & Story Angle</span>
              <p className="detail-text">{activeCampaign.campaign_description}</p>
            </div>

            <div className="detail-item">
              <span className="detail-label">Target Audience</span>
              <p className="detail-text">{activeCampaign.target_audience}</p>
            </div>

            <div className="detail-item">
              <span className="detail-label">Desired Outcome</span>
              <p className="detail-text">{activeCampaign.desired_outcome}</p>
            </div>

            <div className="detail-item full-width">
              <span className="detail-label">Key Topics</span>
              <div className="topic-tags-container">
                {activeCampaign.key_topics
                  .split(/[;,]/)
                  .map((t) => t.trim())
                  .filter(Boolean)
                  .map((topic) => (
                    <span key={topic} className="tag topic-tag">
                      {topic}
                    </span>
                  ))}
              </div>
            </div>
          </div>

          <div className="card-actions-footer">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => navigate('/journalists')}
            >
              Next: Import Journalists &rarr;
            </button>
          </div>
        </div>
      ) : (
        <div className="page-card form-card">
          <div className="form-header-row">
            <h2 className="form-title">Create New Campaign</h2>
            <button
              type="button"
              className="btn btn-secondary btn-sm btn-sample"
              onClick={handleFillSample}
            >
              ✨ Fill Sample Data
            </button>
          </div>

          <form onSubmit={handleSubmit} className="campaign-form" noValidate>
            <div className="form-row">
              <div className="form-group flex-1">
                <label htmlFor="name" className="form-label">
                  Campaign Name <span className="required-star">*</span>
                </label>
                <input
                  id="name"
                  type="text"
                  className={`form-input ${errors.name ? 'input-error' : ''}`}
                  placeholder="e.g. AI Developer Security Platform Launch"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                />
                {errors.name && <span className="field-error">{errors.name}</span>}
              </div>

              <div className="form-group flex-1">
                <label htmlFor="company_name" className="form-label">
                  Company Name <span className="required-star">*</span>
                </label>
                <input
                  id="company_name"
                  type="text"
                  className={`form-input ${errors.company_name ? 'input-error' : ''}`}
                  placeholder="e.g. Acme Security"
                  value={formData.company_name}
                  onChange={(e) => handleInputChange('company_name', e.target.value)}
                />
                {errors.company_name && (
                  <span className="field-error">{errors.company_name}</span>
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="product_description" className="form-label">
                Product / Service Description <span className="required-star">*</span>
              </label>
              <textarea
                id="product_description"
                rows={3}
                className={`form-textarea ${errors.product_description ? 'input-error' : ''}`}
                placeholder="Describe what the product or service does..."
                value={formData.product_description}
                onChange={(e) => handleInputChange('product_description', e.target.value)}
              />
              {errors.product_description && (
                <span className="field-error">{errors.product_description}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="campaign_description" className="form-label">
                Campaign / Story Description <span className="required-star">*</span>
              </label>
              <textarea
                id="campaign_description"
                rows={3}
                className={`form-textarea ${errors.campaign_description ? 'input-error' : ''}`}
                placeholder="What is the story angle or announcement?"
                value={formData.campaign_description}
                onChange={(e) => handleInputChange('campaign_description', e.target.value)}
              />
              {errors.campaign_description && (
                <span className="field-error">{errors.campaign_description}</span>
              )}
            </div>

            <div className="form-row">
              <div className="form-group flex-1">
                <label htmlFor="target_audience" className="form-label">
                  Target Audience <span className="required-star">*</span>
                </label>
                <input
                  id="target_audience"
                  type="text"
                  className={`form-input ${errors.target_audience ? 'input-error' : ''}`}
                  placeholder="e.g. Software engineers, DevOps leads"
                  value={formData.target_audience}
                  onChange={(e) => handleInputChange('target_audience', e.target.value)}
                />
                {errors.target_audience && (
                  <span className="field-error">{errors.target_audience}</span>
                )}
              </div>

              <div className="form-group flex-1">
                <label htmlFor="key_topics" className="form-label">
                  Key Topics <span className="required-star">*</span>
                </label>
                <input
                  id="key_topics"
                  type="text"
                  className={`form-input ${errors.key_topics ? 'input-error' : ''}`}
                  placeholder="e.g. AI; Cybersecurity; Python; Developer Tools"
                  value={formData.key_topics}
                  onChange={(e) => handleInputChange('key_topics', e.target.value)}
                />
                <span className="form-hint">Separate multiple topics with semicolons or commas</span>
                {errors.key_topics && (
                  <span className="field-error">{errors.key_topics}</span>
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="desired_outcome" className="form-label">
                Desired Outcome <span className="required-star">*</span>
              </label>
              <input
                id="desired_outcome"
                type="text"
                className={`form-input ${errors.desired_outcome ? 'input-error' : ''}`}
                placeholder="e.g. Generate press coverage in top-tier tech publications"
                value={formData.desired_outcome}
                onChange={(e) => handleInputChange('desired_outcome', e.target.value)}
              />
              {errors.desired_outcome && (
                <span className="field-error">{errors.desired_outcome}</span>
              )}
            </div>

            <div className="form-actions-row">
              {activeCampaign && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowForm(false)}
                >
                  Cancel
                </button>
              )}
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <LoadingSpinner inline message="Saving Campaign..." size="small" />
                ) : (
                  'Create Campaign'
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
