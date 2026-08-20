import type {
  Analysis,
  ApiErrorResponse,
  Campaign,
  CampaignAnalysisRunResult,
  CampaignCreatePayload,
  HealthResponse,
  Journalist,
  JournalistImportResult,
  Pitch,
} from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

export class ApiRequestError extends Error {
  readonly code: string
  readonly status: number
  readonly details?: unknown

  constructor(message: string, status: number, code: string = 'UNKNOWN_ERROR', details?: unknown) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
    this.details = details
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type')
  const isJson = contentType && contentType.includes('application/json')

  if (!response.ok) {
    if (isJson) {
      try {
        const errorData = (await response.json()) as ApiErrorResponse
        if (errorData?.error) {
          throw new ApiRequestError(
            errorData.error.message || `Request failed with status ${response.status}`,
            response.status,
            errorData.error.code || 'API_ERROR',
            errorData.error.details
          )
        }
      } catch (err) {
        if (err instanceof ApiRequestError) throw err
      }
    }
    throw new ApiRequestError(
      `Request failed with status ${response.status} (${response.statusText})`,
      response.status
    )
  }

  if (isJson) {
    return (await response.json()) as T
  }

  return (await response.text()) as unknown as T
}

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`
  const headers = new Headers(options.headers || {})

  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })
    return await handleResponse<T>(response)
  } catch (error) {
    if (error instanceof ApiRequestError) {
      throw error
    }
    throw new ApiRequestError(
      error instanceof Error ? error.message : 'Unable to communicate with the server',
      0,
      'NETWORK_ERROR'
    )
  }
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    }),
  put: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),
}

export async function checkBackendHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}

// Campaign API endpoints
export async function createCampaign(data: CampaignCreatePayload): Promise<Campaign> {
  return apiClient.post<Campaign>('/api/campaigns', data)
}

export async function getCampaign(campaignId: string): Promise<Campaign> {
  return apiClient.get<Campaign>(`/api/campaigns/${campaignId}`)
}

export async function updateCampaign(
  campaignId: string,
  data: CampaignCreatePayload
): Promise<Campaign> {
  return apiClient.put<Campaign>(`/api/campaigns/${campaignId}`, data)
}

export async function listCampaigns(): Promise<Campaign[]> {
  return apiClient.get<Campaign[]>('/api/campaigns')
}

// Journalist API endpoints
export async function listJournalists(campaignId: string): Promise<Journalist[]> {
  return apiClient.get<Journalist[]>(`/api/campaigns/${campaignId}/journalists`)
}

export async function getJournalist(campaignId: string, journalistId: string): Promise<Journalist> {
  return apiClient.get<Journalist>(`/api/campaigns/${campaignId}/journalists/${journalistId}`)
}

export async function importJournalistsCsv(
  campaignId: string,
  file: File
): Promise<JournalistImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post<JournalistImportResult>(
    `/api/campaigns/${campaignId}/journalists/import`,
    formData
  )
}

// Analysis API endpoints
export async function runCampaignAnalysis(campaignId: string): Promise<CampaignAnalysisRunResult> {
  return apiClient.post<CampaignAnalysisRunResult>(`/api/campaigns/${campaignId}/analysis`)
}

export async function listAnalyses(campaignId: string): Promise<Analysis[]> {
  return apiClient.get<Analysis[]>(`/api/campaigns/${campaignId}/analysis`)
}

export async function getAnalysisForJournalist(
  campaignId: string,
  journalistId: string
): Promise<Analysis> {
  return apiClient.get<Analysis>(`/api/campaigns/${campaignId}/analysis/${journalistId}`)
}

// Pitch API endpoints
export async function generatePitch(campaignId: string, journalistId: string): Promise<Pitch> {
  return apiClient.post<Pitch>(`/api/campaigns/${campaignId}/journalists/${journalistId}/pitch`)
}

export async function getPitchForJournalist(
  campaignId: string,
  journalistId: string
): Promise<Pitch> {
  return apiClient.get<Pitch>(`/api/campaigns/${campaignId}/journalists/${journalistId}/pitch`)
}
