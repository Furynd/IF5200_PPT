import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from './api'
import { getToken, setToken, clearToken } from './token'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // On mount, try to restore session from stored token
  useEffect(() => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }

    api.me()
      .then(data => setUser(data))
      .catch(() => {
        clearToken()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await api.login({ email, password })
    setToken(data.access_token)
    const me = await api.me()
    setUser(me)
    return me
  }, [])

  const register = useCallback(async (form) => {
    await api.register(form)
    // Auto-login after register
    return login(form.email, form.password)
  }, [login])

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
