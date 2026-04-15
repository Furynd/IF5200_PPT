import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Home, Search, Send, User, Settings, LogOut } from 'lucide-react'

const navItems = [
  { to: '/', icon: Home, label: 'Beranda' },
  { to: '/search', icon: Search, label: 'Cari Perusahaan' },
  { to: '/referrals', icon: Send, label: 'Referral Saya' },
  { to: '/profile', icon: User, label: 'Profil' },
  { to: '/settings', icon: Settings, label: 'Pengaturan' },
]

export default function Layout() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top navbar */}
      <header className="bg-white border-b border-surface-200 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <NavLink to="/" className="text-xl font-bold text-primary-600">Referly</NavLink>
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                    isActive ? 'bg-primary-50 text-primary-700 font-medium' : 'text-gray-600 hover:bg-surface-100'
                  }`
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
            <button onClick={handleLogout} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-red-50 hover:text-red-600 ml-2">
              <LogOut size={18} />
            </button>
          </nav>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-surface-200 flex justify-around py-2 z-50">
        {navItems.slice(0, 4).map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-0.5 text-xs ${isActive ? 'text-primary-600' : 'text-gray-500'}`
            }
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
