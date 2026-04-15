import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50">
        <div className="text-gray-400 text-sm">Memuat...</div>
      </div>
    )
  }

  if (!user) {
    // Remember where the user was trying to go so we can send them back after login
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}
