import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Send the user back to where they were trying to go, or home
  const from = location.state?.from?.pathname || '/'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.message || 'Email atau password salah')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center text-primary-600 mb-2">Referly</h1>
        <p className="text-center text-gray-500 mb-8">Temukan koneksi, dapatkan referral</p>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-surface-200 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={loading}
              className="w-full px-3 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              disabled={loading}
              className="w-full px-3 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Masuk...' : 'Masuk'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Belum punya akun?{' '}
          <Link to="/register" className="text-primary-600 font-medium hover:underline">Daftar</Link>
        </p>
      </div>
    </div>
  )
}
