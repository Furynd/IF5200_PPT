import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Network, Settings, LogOut } from 'lucide-react'
import { useAuth } from '../lib/auth'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = user?.full_name
    ?.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?'

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar */}
      <aside className="w-56 min-h-screen bg-slate-900 flex flex-col fixed left-0 top-0 bottom-0 z-40">
        {/* Logo */}
        <div className="px-5 pt-6 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-indigo-500 rounded-md flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-bold">R</span>
            </div>
            <div className="leading-tight">
              <span className="text-white font-bold text-sm">Referly</span>
              <span className="text-slate-400 text-xs ml-1">Professional</span>
            </div>
          </div>
          <p className="text-xs text-slate-600 font-semibold tracking-widest uppercase mt-1.5 ml-9">Premium Network</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-0.5">
          <NavLink
            to="/network"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <Network size={16} />
            Network
          </NavLink>

          <div className="pt-5 pb-1.5 px-3">
            <span className="text-xs font-semibold text-slate-600 uppercase tracking-widest">System</span>
          </div>

          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <Settings size={16} />
            Settings
          </NavLink>

        </nav>

        {/* Logout at bottom */}
        <div className="px-3 pb-5">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-500 hover:text-red-400 hover:bg-slate-800 transition-colors"
          >
            <LogOut size={16} />
            Log Out
          </button>
        </div>
      </aside>

      {/* Main area */}
      <div className="flex-1 ml-56 flex flex-col min-h-screen">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-30 px-6 h-14 flex items-center justify-end">
          <NavLink
            to="/profile"
            className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-semibold hover:bg-slate-700 transition-colors"
            title={user?.email}
          >
            {initials}
          </NavLink>
        </header>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
