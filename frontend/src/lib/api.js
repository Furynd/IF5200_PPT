const API_BASE = '/api'

export function getToken() {
  return localStorage.getItem('token')
}

export function setToken(token) {
  localStorage.setItem('token', token)
}

export function clearToken() {
  localStorage.removeItem('token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    clearToken()
    window.location.href = '/login'
    return
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

  return res.json()
}

export const api = {
  // Auth
  login: (data) => request('/auth/dev-login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data) => request('/auth/dev-register', { method: 'POST', body: JSON.stringify(data) }),
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
