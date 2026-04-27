import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from './api'
import { getToken, setToken, clearToken } from './token'
import { hasSupabaseConfig, supabase } from './supabase'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const syncAndFetchUser = useCallback(async (authUser, accessToken) => {
    if (authUser) {
      const syncHeaders = accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined

      await api.syncAuthProfile({
        email: authUser.email,
        full_name: authUser.user_metadata?.full_name ?? null,
        phone_number: authUser.user_metadata?.phone_number ?? null,
      }, syncHeaders)
    }

    const me = await api.me()
    setUser(me)
    return me
  }, [])

  useEffect(() => {
    let mounted = true

    const bootstrap = async () => {
      if (!hasSupabaseConfig || !supabase) {
        const token = getToken()
        if (!token) {
          if (mounted) setLoading(false)
          return
        }

        api.me()
          .then((data) => {
            if (!mounted) return
            setUser(data)
          })
          .catch(() => {
            clearToken()
            if (!mounted) return
            setUser(null)
          })
          .finally(() => {
            if (mounted) setLoading(false)
          })
        return
      }

      try {
        const { data } = await supabase.auth.getSession()
        const session = data?.session

        if (!session?.access_token) {
          clearToken()
          if (mounted) {
            setUser(null)
            setLoading(false)
          }
          return
        }

        setToken(session.access_token)
        await syncAndFetchUser(session.user, session.access_token)
      } catch {
        clearToken()
        if (mounted) setUser(null)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    bootstrap()

    if (!hasSupabaseConfig || !supabase) {
      return () => {
        mounted = false
      }
    }

    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'SIGNED_OUT' || !session?.access_token) {
          clearToken()
          if (mounted) setUser(null)
          return
        }

        setToken(session.access_token)
        try {
          await syncAndFetchUser(session.user, session.access_token)
        } catch {
          clearToken()
          if (mounted) setUser(null)
        }
      }
    )

    return () => {
      mounted = false
      authListener.subscription.unsubscribe()
    }
  }, [syncAndFetchUser])

  const login = useCallback(async (email, password) => {
    if (!hasSupabaseConfig || !supabase) {
      const data = await api.login({ email, password })
      setToken(data.access_token)
      const me = await api.me()
      setUser(me)
      return me
    }

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) throw new Error(error.message)
    if (!data.session?.access_token) throw new Error('No Supabase session found')

    setToken(data.session.access_token)
    return syncAndFetchUser(data.user, data.session.access_token)
  }, [syncAndFetchUser])

  const register = useCallback(async (form) => {
    if (!hasSupabaseConfig || !supabase) {
      await api.register(form)
      return login(form.email, form.password)
    }

    const { data, error } = await supabase.auth.signUp({
      email: form.email,
      password: form.password,
      options: {
        data: {
          full_name: form.full_name,
          phone_number: form.phone_number,
        },
      },
    })

    if (error) throw new Error(error.message)

    if (!data.session?.access_token) {
      return { needsEmailConfirmation: true }
    }

    setToken(data.session.access_token)
    await syncAndFetchUser(data.user, data.session.access_token)
    return { needsEmailConfirmation: false }
  }, [login, syncAndFetchUser])

  const loginWithProvider = useCallback(async (provider) => {
    if (!hasSupabaseConfig || !supabase) {
      throw new Error('Supabase OAuth is not configured')
    }

    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/login`,
      },
    })

    if (error) throw new Error(error.message)
  }, [])

  const logout = useCallback(() => {
    if (hasSupabaseConfig && supabase) {
      supabase.auth.signOut()
    }
    clearToken()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginWithProvider, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
