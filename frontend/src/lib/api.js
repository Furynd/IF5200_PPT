const API_BASE = '/api'

async function request(path, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    return
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
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
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
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
  getConnectionsAtCompany: (companyId, maxHops = 2) =>
    request(`/connections/at-company/${companyId}?max_hops=${maxHops}`),

  // CV
  uploadCV: (file) => uploadFile('/cv/upload', file),
  getUserCV: () => request('/cv/user').catch(() => null),
  extractSkillsFromPDF: (file) => uploadFile('/cv/extract-skills/pdf', file),
  extractSkillsFromText: (cvText) =>
    request('/cv/extract-skills', { method: 'POST', body: JSON.stringify({ cv_text: cvText }) }),

  // Referrals (Week 5)
  sendReferral: (data) => request('/referrals', { method: 'POST', body: JSON.stringify(data) }),
  getReferrals: () => request('/referrals'),
  respondReferral: (id, status) =>
    request(`/referrals/${id}/respond`, { method: 'PUT', body: JSON.stringify({ status }) }),
}
