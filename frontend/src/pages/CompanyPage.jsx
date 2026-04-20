import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Building2, Users, Send, ArrowLeft, Loader2, AlertCircle, UserCheck, UserX } from 'lucide-react'
import { api } from '../lib/api'

export default function CompanyPage() {
  const { id } = useParams()
  const [company, setCompany] = useState(null)
  const [connections, setConnections] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return

    let cancelled = false
    setLoading(true)
    setError('')

    // Fetch connections at this company (also returns company info)
    api.getConnectionsAtCompany(id)
      .then(data => {
        if (cancelled) return
        setCompany(data.company)
        setConnections(data.connections || [])
      })
      .catch(err => {
        if (!cancelled) setError(err.message || 'Gagal memuat data perusahaan')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [id])

  if (loading) {
    return (
      <div className="py-20 text-center">
        <Loader2 size={32} className="mx-auto text-gray-300 animate-spin mb-2" />
        <p className="text-gray-500 text-sm">Memuat data perusahaan...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
        <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-medium text-red-900">Gagal memuat</p>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      </div>
    )
  }

  if (!company) return null

  // Split connections by hop distance for better display
  const directConnections = connections.filter(c => c.hops === 1)
  const secondDegreeConnections = connections.filter(c => c.hops === 2)

  return (
    <div className="space-y-6">
      <Link to="/search" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={16} /> Kembali ke pencarian
      </Link>

      {/* Company header */}
      <div className="bg-white rounded-xl border border-surface-200 p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0">
            <Building2 size={28} className="text-primary-600" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl font-bold text-gray-900">{company.name}</h1>
            {company.industry && <p className="text-gray-500">{company.industry}</p>}
          </div>
        </div>
      </div>

      {/* Connections */}
      {connections.length === 0 ? (
        <EmptyConnections />
      ) : (
        <>
          {directConnections.length > 0 && (
            <ConnectionList
              title="Koneksi Langsung"
              subtitle="Orang yang kamu kenal secara langsung"
              connections={directConnections}
              companyId={company.id}
              companyName={company.name}
            />
          )}
          {secondDegreeConnections.length > 0 && (
            <ConnectionList
              title="Koneksi Tidak Langsung"
              subtitle="Bisa dijangkau melalui satu teman perantara"
              connections={secondDegreeConnections}
              companyId={company.id}
              companyName={company.name}
            />
          )}
        </>
      )}
    </div>
  )
}

function ConnectionList({ title, subtitle, connections, companyId, companyName }) {
  return (
    <div className="bg-white rounded-xl border border-surface-200 p-6">
      <div className="mb-4">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <Users size={18} /> {title}
          <span className="text-sm font-normal text-gray-500">({connections.length})</span>
        </h2>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </div>
      <ul className="divide-y divide-surface-200 -mx-6">
        {connections.map(conn => (
          <ConnectionItem
            key={conn.user.id}
            conn={conn}
            companyId={companyId}
            companyName={companyName}
          />
        ))}
      </ul>
    </div>
  )
}

function ConnectionItem({ conn, companyId, companyName }) {
  const { user, job_title, hops, path_via, is_open_to_refer } = conn

  return (
    <li className="px-6 py-3 flex items-center justify-between gap-4">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="font-medium text-gray-900 truncate">{user.full_name}</p>
          {hops === 1 ? (
            <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full flex-shrink-0">Langsung</span>
          ) : (
            <span className="text-xs bg-surface-100 text-gray-600 px-2 py-0.5 rounded-full flex-shrink-0">2 hop</span>
          )}
        </div>
        {job_title && <p className="text-sm text-gray-500 truncate">{job_title}</p>}
        {hops === 2 && path_via?.length > 0 && (
          <p className="text-xs text-gray-400 truncate mt-0.5">
            Lewat {path_via.join(', ')}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        {is_open_to_refer ? (
          <button
            disabled
            title="Fitur referral akan tersedia di minggu 5"
            className="flex items-center gap-1 px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
          >
            <Send size={14} /> Minta Referral
          </button>
        ) : (
          <span
            title="Pengguna ini menutup referral saat ini"
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-gray-400"
          >
            <UserX size={14} /> Tidak tersedia
          </span>
        )}
      </div>
    </li>
  )
}

function EmptyConnections() {
  return (
    <div className="bg-white rounded-xl border border-surface-200 p-8 text-center">
      <Users size={40} className="mx-auto text-gray-300 mb-3" />
      <p className="font-medium text-gray-700">Belum ada koneksi di perusahaan ini</p>
      <p className="text-sm text-gray-500 mt-1 max-w-xs mx-auto">
        Sinkronkan kontak telepon di halaman profil agar kami bisa mencocokkan teman-temanmu.
      </p>
      <Link
        to="/profile"
        className="inline-block mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
      >
        Ke Profil
      </Link>
    </div>
  )
}
