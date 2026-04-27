import { Link, useLocation } from 'react-router-dom'

export default function PublicNavbar() {
  const { pathname } = useLocation()

  const links = [
    { to: '/', label: 'Home' },
    { to: '/about', label: 'About' },
    { to: '/register', label: 'Registration' },
  ]

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="font-bold text-slate-900 text-xl">Referly</Link>

        <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`hover:text-slate-900 transition-colors ${
                pathname === to ? 'font-semibold text-slate-900 border-b-2 border-slate-900 pb-0.5' : ''
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-slate-900 transition-colors">
            Login
          </Link>
          <Link
            to="/register"
            className="text-sm font-semibold bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </header>
  )
}
