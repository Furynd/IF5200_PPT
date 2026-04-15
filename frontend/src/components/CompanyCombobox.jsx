import { useState, useEffect, useRef } from 'react'
import { Search, Check, Loader2 } from 'lucide-react'
import { api } from '../lib/api'

// Debounce hook to avoid spamming the API on every keystroke
function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

export default function CompanyCombobox({ value, onChange, disabled }) {
  const [query, setQuery] = useState(value?.name || '')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const containerRef = useRef(null)

  const debouncedQuery = useDebounce(query, 300)

  // Fetch companies when query changes
  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setResults([])
      return
    }
    if (value && debouncedQuery === value.name) return // Don't re-search after selecting

    let cancelled = false
    setLoading(true)
    api.searchCompanies(debouncedQuery)
      .then(data => { if (!cancelled) setResults(data.companies || []) })
      .catch(() => { if (!cancelled) setResults([]) })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [debouncedQuery, value])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const handleSelect = (company) => {
    onChange(company)
    setQuery(company.name)
    setOpen(false)
  }

  const handleChange = (e) => {
    setQuery(e.target.value)
    setOpen(true)
    if (value && e.target.value !== value.name) {
      onChange(null)
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => setOpen(true)}
          disabled={disabled}
          placeholder="Cari nama perusahaan..."
          className="w-full pl-10 pr-10 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
        />
        {loading && (
          <Loader2 size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 animate-spin" />
        )}
      </div>

      {open && (query.length >= 2) && (
        <div className="absolute z-10 mt-1 w-full bg-white border border-surface-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {loading && results.length === 0 && (
            <div className="px-3 py-3 text-sm text-gray-400 text-center">Mencari...</div>
          )}
          {!loading && results.length === 0 && (
            <div className="px-3 py-3 text-sm text-gray-400 text-center">
              Tidak ditemukan. Coba kata kunci lain.
            </div>
          )}
          {results.map(company => {
            const isSelected = value?.id === company.id
            return (
              <button
                key={company.id}
                type="button"
                onClick={() => handleSelect(company)}
                className={`w-full text-left px-3 py-2 hover:bg-surface-50 flex items-center justify-between gap-2 ${
                  isSelected ? 'bg-primary-50' : ''
                }`}
              >
                <div className="min-w-0">
                  <p className="font-medium text-gray-900 truncate">{company.name}</p>
                  {company.industry && (
                    <p className="text-xs text-gray-500 truncate">{company.industry}</p>
                  )}
                </div>
                {isSelected && <Check size={16} className="text-primary-600 flex-shrink-0" />}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
