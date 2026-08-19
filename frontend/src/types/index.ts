export interface HealthResponse {
  status: string
  database?: string
}

export interface ApiError {
  code: string
  message: string
  details?: unknown
}

export interface ApiErrorResponse {
  error: ApiError
}

export interface CampaignCreatePayload {
  name: string
  company_name: string
  product_description: string
  campaign_description: string
  target_audience: string
  key_topics: string
  desired_outcome: string
}

export interface Campaign {
  id: string
  name: string
  company_name: string
  product_description: string
  campaign_description: string
  target_audience: string
  key_topics: string
  desired_outcome: string
  created_at: string
}

export interface Journalist {
  id: string
  campaign_id: string
  name: string
  email: string
  publication: string
  role: string
  topics: string
  bio: string
  recent_articles: string
  created_at?: string
}

export interface JournalistImportRowError {
  row: number
  message: string
}

export interface JournalistImportResult {
  imported_count: number
  total_rows: number
  errors: JournalistImportRowError[]
  journalists: Journalist[]
}

export type AnalysisPriority = 'high' | 'medium' | 'low'

export interface Analysis {
  id: string
  campaign_id: string
  journalist_id: string
  score: number
  priority: AnalysisPriority
  reasons: string[]
  supporting_evidence: string[]
  concerns: string[]
  created_at?: string
}

export interface Pitch {
  id: string
  campaign_id: string
  journalist_id: string
  subject: string
  body: string
  created_at?: string
}

export type LoadingStatus = 'idle' | 'loading' | 'success' | 'error'

export interface AsyncState<T> {
  status: LoadingStatus
  data: T | null
  error: string | null
}
