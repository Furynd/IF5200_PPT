import { useState, useEffect, useMemo } from 'react'
import { Search, Users, Send, ArrowRight, UserCheck, UserX, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

function HopBadge({ hops }) {
  return hops === 1
    ? <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-green-100 text-green-700">1st degree</span>
    : <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">2nd degree</span>
}

function ConnectionCard({ conn }) {
  const initials = conn.user.full_name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
  return (
    <div className="flex gap-3 items-start py-3 border-b border-gray-100 last:border-0">
      <div className="flex-shrink-0 w-9 h-9 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs font-semibold">
        {initials}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-gray-900 text-sm">{conn.user.full_name}</span>
          <HopBadge hops={conn.hops} />
          {conn.is_open_to_refer
            ? <span className="flex items-center gap-0.5 text-xs text-green-600"><UserCheck size={11} /> Open to refer</span>
            : <span className="flex items-center gap-0.5 text-xs text-gray-400"><UserX size={11} /> Not referring</span>
          }
        </div>
        {(conn.job_title || conn.company_name) && (
          <p className="text-xs text-gray-500 mt-0.5 truncate">
            {[conn.job_title, conn.company_name].filter(Boolean).join(' at ')}
          </p>
        )}
        {conn.hops === 2 && conn.path_via?.length > 0 && (
          <p className="text-xs text-gray-400 mt-0.5">via {conn.path_via.join(' → ')}</p>
        )}
        {conn.skills?.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1.5">
            {conn.skills.slice(0, 3).map(s => (
              <span key={s.id} className="text-xs px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500">{s.name}</span>
            ))}
            {conn.skills.length > 3 && (
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-400">+{conn.skills.length - 3}</span>
            )}
          </div>
        )}
      </div>
      {conn.is_open_to_refer && (
        <button className="flex-shrink-0 flex items-center gap-0.5 text-xs font-medium text-primary-600 hover:text-primary-700 mt-0.5">
          Minta Referral <ChevronRight size={11} />
        </button>
      )}
    </div>
  )
}

export default function HomePage() {
  const [connections, setConnections] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [filterHops, setFilterHops] = useState('all')

  useEffect(() => {
    let cancelled = false
    Promise.all([api.getConnections(), api.getNetworkStats()])
      .then(([connData, statsData]) => {
        if (cancelled) return
        setConnections(connData.connections)
        setStats(statsData)
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  const filtered = useMemo(() => {
    let list = connections
    if (filterHops !== 'all') list = list.filter(c => c.hops === parseInt(filterHops, 10))
    if (query.trim()) {
      const q = query.toLowerCase()
      list = list.filter(c =>
        c.user.full_name.toLowerCase().includes(q) ||
        c.company_name?.toLowerCase().includes(q) ||
        c.job_title?.toLowerCase().includes(q) ||
        c.skills?.some(s => s.name.toLowerCase().includes(q))
      )
    }
    return list
  }, [connections, query, filterHops])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Selamat datang di Referly</h1>
        <p className="text-gray-500 mt-1">Temukan siapa yang kamu kenal di perusahaan impianmu.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { to: '/search', icon: Search, title: 'Cari Perusahaan', desc: 'Lihat koneksimu di perusahaan target', color: 'bg-blue-50 text-blue-600' },
          { to: '/profile', icon: Users, title: 'Sinkronkan Kontak', desc: 'Hubungkan buku kontakmu', color: 'bg-green-50 text-green-600' },
          { to: '/referrals', icon: Send, title: 'Referral Saya', desc: 'Lihat status permintaan referral', color: 'bg-purple-50 text-purple-600' },
        ].map(({ to, icon: Icon, title, desc, color }) => (
          <Link key={to} to={to} className="bg-white rounded-xl border border-surface-200 p-5 hover:shadow-md transition-shadow group">
            <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center mb-3`}><Icon size={20} /></div>
            <h3 className="font-semibold text-gray-900 flex items-center gap-1">{title}<ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" /></h3>
            <p className="text-sm text-gray-500 mt-1">{desc}</p>
          </Link>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-surface-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Ringkasan Jaringanmu</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          {[
            { v: stats ? stats.connections : '--', l: 'Koneksi' },
            { v: stats ? stats.companies : '--', l: 'Perusahaan' },
            { v: stats ? stats.referrals_sent : '--', l: 'Referral Terkirim' },
          ].map(({ v, l }) => (
            <div key={l}>
              <p className="text-3xl font-bold text-primary-600">{v}</p>
              <p className="text-sm text-gray-500">{l}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-surface-200 p-6">
        <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
          <h2 className="font-semibold text-gray-900">Jaringanmu</h2>
          <div className="flex gap-2">
            <div className="relative">
              <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Cari nama, perusahaan, skill..."
                value={query}
                onChange={e => setQuery(e.target.value)}
                className="pl-7 pr-3 py-1.5 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 w-48"
              />
            </div>
            <select
              value={filterHops}
              onChange={e => setFilterHops(e.target.value)}
              className="text-xs border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
            >
              <option value="all">Semua</option>
              <option value="1">1st degree</option>
              <option value="2">2nd degree</option>
            </select>
          </div>
        </div>

        {loading && <p className="text-sm text-gray-400 text-center py-8">Memuat jaringanmu...</p>}

        {!loading && filtered.length === 0 && (
          <p className="text-sm text-gray-400 text-center py-8">
            {connections.length === 0 ? 'Belum ada koneksi ditemukan.' : 'Tidak ada hasil yang cocok.'}
          </p>
        )}

        {!loading && filtered.length > 0 && (
          <>
            <p className="text-xs text-gray-400 mb-2">{filtered.length} orang · diurutkan berdasarkan relevansi</p>
            {filtered.map(conn => <ConnectionCard key={conn.user.id} conn={conn} />)}
          </>
        )}
      </div>
    </div>
  )
}
