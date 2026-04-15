import { useState } from 'react'
import { Search } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  const handleSearch = (e) => {
    e.preventDefault()
    // TODO: integrate with api.searchCompanies(query) in Week 4
    setResults([
      { id: 'comp-001', name: 'PT GoTo Gojek Tokopedia Tbk', industry: 'Technology', connections: 3 },
      { id: 'comp-021', name: 'Bank Central Asia (BCA)', industry: 'Banking', connections: 1 },
    ])
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Cari Perusahaan</h1>
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"/>
          <input type="text" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Ketik nama perusahaan..." className="w-full pl-10 pr-4 py-2.5 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"/>
        </div>
        <button type="submit" className="px-5 py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700">Cari</button>
      </form>
      {results.length > 0 && <div className="space-y-2">
        {results.map(c=>(
          <Link key={c.id} to={`/company/${c.id}`} className="block bg-white rounded-lg border border-surface-200 p-4 hover:shadow-sm transition-shadow">
            <div className="flex items-center justify-between">
              <div><h3 className="font-semibold text-gray-900">{c.name}</h3><p className="text-sm text-gray-500">{c.industry}</p></div>
              <span className="text-sm font-medium text-primary-600 bg-primary-50 px-3 py-1 rounded-full">{c.connections} koneksi</span>
            </div>
          </Link>
        ))}
      </div>}
    </div>
  )
}