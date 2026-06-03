import { useState, useEffect } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const debouncedQuery = useDebounce(query, 400)

  // Auto-search as the user types (after debounce)
  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.trim().length < 2) {
      setResults([])
      setSearched(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError('')

    api.searchCompanies(debouncedQuery)
      .then(data => {
        if (!cancelled) {
          setResults(data.companies || [])
          setSearched(true)
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.message || 'Gagal mencari perusahaan')
          setResults([])
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [debouncedQuery])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Cari Perusahaan</h1>
        <p className="text-gray-500 text-sm mt-1">Temukan perusahaan dan lihat koneksimu di sana.</p>
      </div>

      <div className="relative">
        <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ketik nama perusahaan..."
          autoFocus
          className="w-full pl-10 pr-10 py-3 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-base"
        />
        {loading && (
          <Loader2 size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 animate-spin" />
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">{error}</div>
      )}

      {/* Results */}
      {searched && results.length === 0 && !loading && (
        <div className="bg-white rounded-xl border border-surface-200 p-8 text-center">
          <Search size={32} className="mx-auto text-gray-300 mb-2" />
          <p className="text-gray-500">Tidak ditemukan perusahaan untuk "{debouncedQuery}"</p>
          <p className="text-sm text-gray-400 mt-1">Coba kata kunci lain atau periksa ejaan.</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-2">
          {results.map(company => (
            <Link
              key={company.id}
              to={`/company/${company.id}`}
              className="block bg-white rounded-lg border border-surface-200 p-4 hover:shadow-sm transition-shadow"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{company.name}</h3>
                  {company.industry && (
                    <p className="text-sm text-gray-500 truncate">{company.industry}</p>
                  )}
                </div>
                <ConnectionBadge count={company.connection_count} />
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Empty initial state */}
      {!searched && !loading && query.length < 2 && (
        <div className="bg-white rounded-xl border border-surface-200 p-8 text-center">
          <Search size={32} className="mx-auto text-gray-300 mb-2" />
          <p className="text-gray-500">Mulai mengetik untuk mencari perusahaan.</p>
        </div>
      )}
    </div>
  )
}

function ConnectionBadge({ count }) {
  if (count === 0 || count === undefined || count === null) {
    return (
      <span className="text-xs text-gray-400 bg-surface-100 px-2 py-1 rounded-full flex-shrink-0">
        Tidak ada koneksi
      </span>
    )
  }
  return (
    <span className="text-sm font-medium text-primary-600 bg-primary-50 px-3 py-1 rounded-full flex-shrink-0">
      {count} pengguna
    </span>
  )
}
