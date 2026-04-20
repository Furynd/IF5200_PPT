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

  // Companies
  searchCompanies: (q) => request(`/companies/search?q=${encodeURIComponent(q)}`),
  getCompany: (id) => request(`/companies/${id}`),

  // Connections
  syncContacts: (hashes) => request('/contacts/sync', { method: 'POST', body: JSON.stringify({ hashes }) }),
  getConnectionsAtCompany: (companyId) => request(`/connections/at-company/${companyId}`),

  // Referrals
  sendReferral: (data) => request('/referrals', { method: 'POST', body: JSON.stringify(data) }),
  getReferrals: () => request('/referrals'),
  respondReferral: (id, status) => request(`/referrals/${id}/respond`, { method: 'PUT', body: JSON.stringify({ status }) }),
}
