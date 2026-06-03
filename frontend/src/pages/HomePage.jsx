import { useState, useEffect, useMemo } from 'react'
import { Search, Plus, MapPin, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'

const PAGE_SIZE = 6

function Avatar({ name, size = 'md' }) {
  const initials = name?.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?'
  const colors = ['bg-blue-500', 'bg-emerald-500', 'bg-purple-500', 'bg-orange-500', 'bg-pink-500', 'bg-teal-500']
  const color = colors[(name?.charCodeAt(0) || 0) % colors.length]
  const sizeClass = size === 'sm' ? 'w-7 h-7 text-xs' : size === 'lg' ? 'w-14 h-14 text-lg' : 'w-12 h-12 text-sm'
  return (
    <div className={`${sizeClass} ${color} rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0`}>
      {initials}
    </div>
  )
}

function ConnectionCard({ conn }) {
  const isOnline = conn.hops === 1
  const companyId = conn.company_id || null

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <Link
          to={`/network/${conn.user.id}`}
          state={{ connection: conn }}
          className="flex items-start gap-3 min-w-0 flex-1 group"
        >
          <div className="relative flex-shrink-0">
            <Avatar name={conn.user.full_name} />
            <span className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${isOnline ? 'bg-emerald-500' : 'bg-gray-300'}`} />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-semibold text-slate-900 truncate group-hover:text-primary-700 transition-colors">{conn.user.full_name}</p>
            <p className="text-xs text-gray-500 truncate mt-0.5">
              {[conn.job_title, conn.company_name].filter(Boolean).join(' at ')}
            </p>
            {conn.hops === 2 && conn.path_via?.length > 0 && (
              <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
                <MapPin size={10} />
                via {conn.path_via[0]}
              </p>
            )}
          </div>
        </Link>
      </div>

      {/* Mutual connection avatars */}
      {conn.skills?.length > 0 && (
        <div className="flex items-center gap-1.5">
          <div className="flex -space-x-1.5">
            {conn.skills.slice(0, 3).map((s, i) => (
              <div key={i} className="w-6 h-6 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center">
                <span className="text-gray-500 text-[8px] font-bold">{s.name[0]}</span>
              </div>
            ))}
          </div>
          {conn.skills.length > 3 && (
            <span className="text-xs text-gray-400">+{conn.skills.length - 3}</span>
          )}
        </div>
      )}

      {companyId ? (
        <Link
          to={`/company/${companyId}`}
          className="mt-auto w-full py-2 bg-slate-900 text-white text-sm font-semibold rounded-lg hover:bg-slate-800 transition-colors text-center"
        >
          View Jobs
        </Link>
      ) : (
        <button
          disabled
          className="mt-auto w-full py-2 bg-gray-100 text-gray-400 text-sm font-semibold rounded-lg cursor-not-allowed text-center"
        >
          View Jobs
        </button>
      )}
    </div>
  )
}

function RecommendationCard({ item }) {
  const connection = item.connection
  const score = item.score

  return (
    <Link
      to={`/network/${connection?.user?.id || item.user_id}`}
      state={{ connection, recommendation: item }}
      className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow block"
    >
      <div className="flex items-start gap-3">
        <Avatar name={connection?.user?.full_name || item.user_id} size="sm" />
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-slate-900 truncate">
            {connection?.user?.full_name || item.user_id}
          </p>
          <p className="text-xs text-gray-500 mt-0.5 truncate">
            {connection?.job_title || 'Recommended connection'}
          </p>
        </div>
        {/* <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
          {typeof score === 'number' ? score.toFixed(2) : 'N/A'}
        </span> */}
      </div>
      {connection?.company_name && (
        <p className="mt-3 text-xs text-gray-500 truncate">
          {connection.company_name}
        </p>
      )}
    </Link>
  )
}

function AddConnectionModal({ open, onClose, directRecommendations, suggestedRecommendations }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 w-full max-w-3xl bg-white rounded-2xl border border-slate-200 shadow-2xl overflow-hidden max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between gap-4 px-6 py-5 border-b border-slate-200">
          <div>
            <h3 className="text-xl font-bold text-slate-900">Add New Connection</h3>
            <p className="text-sm text-slate-500 mt-1">Recommended connections for you.</p>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50"
            aria-label="Close add connection modal"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <section className="rounded-2xl border border-slate-200 bg-white p-5">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div>
                <h4 className="text-base font-bold text-slate-900">Suggested Connections</h4>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                {suggestedRecommendations.length} hasil
              </span>
            </div>
            {suggestedRecommendations.length === 0 ? (
              <div className="py-8 text-center">
                <p className="font-semibold text-slate-700">Belum ada rekomendasi</p>
                <p className="mt-1 text-sm text-slate-500">
                  Lengkapi profil dan sinkronkan kontak untuk menemukan koneksi yang relevan.
                </p>
              </div>
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {suggestedRecommendations.map((item) => (
                  <RecommendationCard key={item.user_id} item={item} />
                ))}
              </div>
            )}
          </section>

          {/* <section className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5">
            <h4 className="text-base font-bold text-slate-900">Contact Sync</h4>
            <p className="text-sm text-slate-500 mt-1">
              Contact sync is disabled for now while this modal is used for recommendations.
            </p>
            <button
              type="button"
              disabled
              className="mt-4 inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-400 cursor-not-allowed"
            >
              Disabled
            </button>
          </section> */}
        </div>
      </div>
    </div>
  )
}

export default function HomePage() {
  const { user } = useAuth()
  const [connections, setConnections] = useState([])
  const [recommendedConnections, setRecommendedConnections] = useState([])
  const [suggestedConnections, setSuggestedConnections] = useState([])
  const [loading, setLoading] = useState(true)
  const [recommendationLoading, setRecommendationLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [filterHops, setFilterHops] = useState('all')
  const [page, setPage] = useState(1)
  const [syncOpen, setSyncOpen] = useState(false)

  useEffect(() => {
    let cancelled = false
    api.getConnections()
      .then(data => { if (!cancelled) setConnections(data.connections || []) })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    if (!user?.id) return

    let cancelled = false
    setRecommendationLoading(true)

    Promise.all([
      api.getRecommendationConnections(user.id),
      api.getSuggestedRecommendations(user.id),
    ])
      .then(([directData, suggestedData]) => {
        if (cancelled) return
        setRecommendedConnections(directData.connections || [])
        setSuggestedConnections(suggestedData.connections || [])
      })
      .catch(() => {
        if (!cancelled) {
          setRecommendedConnections([])
          setSuggestedConnections([])
        }
      })
      .finally(() => {
        if (!cancelled) setRecommendationLoading(false)
      })

    return () => { cancelled = true }
  }, [user?.id])

  const connectionByUserId = useMemo(() => {
    const map = new Map()
    connections.forEach((connection) => {
      map.set(connection.user.id, connection)
    })
    return map
  }, [connections])

  const recommendationCards = useMemo(() => {
    const direct = recommendedConnections.map((item) => {
      const connection = connectionByUserId.get(item.user_id) || {
        user: {
          id: item.user_id,
          full_name: item.full_name || 'Unknown User'
        },
        job_title: item.job_title,
        company_name: item.company_name,
        company_id: null,
        company_industry: null,
        is_open_to_refer: true,
        hops: null,
        path_via: [],
        skills: []
      }
      return {
        ...item,
        connection
      }
    })
    const suggested = suggestedConnections.map((item) => {
      const connection = connectionByUserId.get(item.user_id) || {
        user: {
          id: item.user_id,
          full_name: item.full_name || 'Unknown User'
        },
        job_title: item.job_title,
        company_name: item.company_name,
        company_id: null,
        company_industry: null,
        is_open_to_refer: true,
        hops: null,
        path_via: [],
        skills: []
      }
      return {
        ...item,
        connection
      }
    })

    return {
      direct: direct.filter((item) => item.connection || item.user_id),
      suggested: suggested.filter((item) => item.connection || item.user_id),
    }
  }, [connectionByUserId, recommendedConnections, suggestedConnections])

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

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleQueryChange = (e) => { setQuery(e.target.value); setPage(1) }
  const handleFilterChange = (e) => { setFilterHops(e.target.value); setPage(1) }

  return (
    <div className="max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Your Network</h1>
          <p className="text-sm text-gray-500 mt-1">
            Connect with industry experts who can vouch for your skills and fast-track your next career move.
          </p>
        </div>
        <button
          onClick={() => setSyncOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 text-white text-sm font-semibold rounded-xl hover:bg-slate-800 transition-colors flex-shrink-0"
        >
          <Plus size={16} />
          Add New Connection
        </button>
      </div>

      {/* Search + filter */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search your network..."
            value={query}
            onChange={handleQueryChange}
            className="w-full pl-9 pr-3 py-2.5 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 shadow-sm"
          />
        </div>
        <select
          value={filterHops}
          onChange={handleFilterChange}
          className="px-3 py-2.5 border border-gray-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-slate-300 shadow-sm"
        >
          <option value="all">All degrees</option>
          <option value="1">1st degree</option>
          <option value="2">2nd degree</option>
        </select>
      </div>

      {/* Grid */}
      {loading && (
        <div className="grid sm:grid-cols-2 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 h-36 animate-pulse" />
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
            <Search size={24} className="text-gray-400" />
          </div>
          <p className="font-semibold text-slate-900">
            {connections.length === 0 ? 'No connections yet' : 'No results found'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {connections.length === 0
              ? 'Add your first connection to get started.'
              : 'Try a different search term or filter.'}
          </p>
          {connections.length === 0 && (
            <button
              onClick={() => setSyncOpen(true)}
              className="mt-4 px-4 py-2 bg-slate-900 text-white text-sm font-semibold rounded-lg hover:bg-slate-800 transition-colors"
            >
              Add Connection
            </button>
          )}
        </div>
      )}

      {!loading && paginated.length > 0 && (
        <>
          <div className="grid sm:grid-cols-2 gap-4">
            {paginated.map(conn => <ConnectionCard key={conn.user.id} conn={conn} />)}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={14} />
              </button>
              {[...Array(totalPages)].map((_, i) => (
                <button
                  key={i}
                  onClick={() => setPage(i + 1)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                    page === i + 1 ? 'bg-slate-900 text-white' : 'border border-gray-200 hover:bg-gray-50 text-slate-700'
                  }`}
                >
                  {i + 1}
                </button>
              ))}
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          )}
        </>
      )}

      <AddConnectionModal
        open={syncOpen}
        onClose={() => setSyncOpen(false)}
        directRecommendations={recommendationCards.direct.slice(0, 6)}
        suggestedRecommendations={recommendationCards.suggested.slice(0, 50)}
      />
    </div>
  )
}
