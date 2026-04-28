import { getToken, clearToken } from './token'

const API_BASE = '/api'

async function request(path, options = {}) {
  const token = getToken()
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
  const headers = isFormData
    ? { ...options.headers }
    : { 'Content-Type': 'application/json', ...options.headers }
  if (token && !headers['Authorization']) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    clearToken()
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    let message = `HTTP ${res.status}`

    if (typeof err?.detail === 'string') {
      message = err.detail
    } else if (Array.isArray(err?.detail)) {
      // FastAPI validation errors often return detail as an array of objects.
      message = err.detail
        .map((item) => item?.msg)
        .filter(Boolean)
        .join(', ') || message
    } else if (typeof err?.message === 'string') {
      message = err.message
    }

    throw new Error(message)
  }

  return res.status === 204 ? null : res.json()
}

async function uploadFile(path, file) {
  const token = localStorage.getItem('token')
  const formData = new FormData()
  formData.append('file', file)
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { method: 'POST', headers, body: formData })

  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    return
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  return res.json()
}

export const api = {
  // Auth
  login: (data) => request('/auth/dev-login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data) => request('/auth/dev-register', { method: 'POST', body: JSON.stringify(data) }),
  syncAuthProfile: (data) => request('/auth/sync', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/auth/me'),

  // Profile
  getProfile: () => request('/user/profile'),
  updateProfile: (data) => request('/user/profile', { method: 'PUT', body: JSON.stringify(data) }),
  getNetworkStats: () => request('/user/network-stats'),

  // Companies
  searchCompanies: (q, limit = 10) =>
    request(`/companies/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  getCompany: (id) => request(`/companies/${id}`),

  // Contacts & connections
  syncContacts: (hashes) =>
    request('/contacts/sync', { method: 'POST', body: JSON.stringify({ hashes }) }),
  getConnections: (maxHops = 2) =>
    request(`/connections?max_hops=${maxHops}`),
  addConnection: (targetUserId) =>
    request('/connections', { method: 'POST', body: JSON.stringify({ target_user_id: targetUserId }) }),
  getConnectionsAtCompany: (companyId, maxHops = 2) =>
    request(`/connections/at-company/${companyId}?max_hops=${maxHops}`),

  // Recommendations
  getRecommendationConnections: (userId) =>
    request(`/recommendations/${userId}/connections`),
  getSuggestedRecommendations: (userId) =>
    request(`/recommendations/${userId}/suggested-connections`),
  getRecommendationVacanciesFromTarget: (userId, targetUserId) =>
    request(`/recommendations/${userId}/vacancies/from-target/${targetUserId}`),
  getRecommendationConnectionsFromCompany: (userId, companyId) =>
    request(`/recommendations/${userId}/connections/from-company/${companyId}`),
  getSuggestedRecommendationsFromCompany: (userId, companyId) =>
    request(`/recommendations/${userId}/suggested-connections/from-company/${companyId}`),

  // CV
  uploadCV: (file) => uploadFile('/cv/upload', file),
  getUserCV: () => request('/cv/user').catch(() => null),
  extractSkillsFromPDF: (file) => uploadFile('/cv/extract-skills/pdf', file),
  extractSkillsFromText: (cvText) =>
    request('/cv/extract-skills', { method: 'POST', body: JSON.stringify({ cv_text: cvText }) }),

  // Referrals (Week 5)
  sendReferral: (data) => {
    const body = data instanceof FormData
      ? data
      : (() => {
          const formData = new FormData()
          Object.entries(data || {}).forEach(([key, value]) => {
            if (value !== undefined && value !== null) formData.append(key, value)
          })
          return formData
        })()

    return request('/referrals', { method: 'POST', body })
  },
  getReferrals: () => request('/referrals'),
  respondReferral: (id, status) =>
    request(`/referrals/${id}/respond`, { method: 'PUT', body: JSON.stringify({ status }) }),
}
