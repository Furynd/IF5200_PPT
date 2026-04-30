import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Briefcase, Building2, ExternalLink, Loader2, MapPin, Send, Users } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import ReferralRequestModal from '../components/ReferralRequestModal'

const AVATAR_COLORS = ['bg-blue-500', 'bg-emerald-500', 'bg-purple-500', 'bg-orange-500', 'bg-pink-500', 'bg-teal-500']

function Avatar({ name, size = 'lg' }) {
  const initials = name?.split(' ').map((word) => word[0]).slice(0, 2).join('').toUpperCase() || '?'
  const color = AVATAR_COLORS[(name?.charCodeAt(0) || 0) % AVATAR_COLORS.length]
  const sizeClass = size === 'sm' ? 'w-10 h-10 text-sm' : size === 'lg' ? 'w-16 h-16 text-xl' : 'w-12 h-12 text-base'

  return (
    <div className={`${sizeClass} ${color} rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0`}>
      {initials}
    </div>
  )
}

function SectionCard({ title, subtitle, children, className = '' }) {
  return (
    <section className={`rounded-2xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      <div className="mb-4">
        <h2 className="text-base font-bold text-slate-900">{title}</h2>
        {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
      </div>
      {children}
    </section>
  )
}

export default function ConnectionPage() {
  const { user: me } = useAuth()
  const { userId } = useParams()
  const location = useLocation()

  const initialConnection = location.state?.connection || null
  const initialRecommendation = location.state?.recommendation || null

  const [connection, setConnection] = useState(initialConnection)
  const [company, setCompany] = useState(null)
  const [vacancies, setVacancies] = useState([])
  const [loading, setLoading] = useState(!initialConnection)
  const [error, setError] = useState('')
  const [referralOpen, setReferralOpen] = useState(false)
  const [addingConnection, setAddingConnection] = useState(false)
  const [connectionAdded, setConnectionAdded] = useState(false)

  useEffect(() => {
    let cancelled = false

    const loadConnection = async () => {
      setLoading(true)
      setError('')

      try {
        let resolvedConnection = initialConnection

        if (!resolvedConnection) {
          const data = await api.getConnections()
          resolvedConnection = (data.connections || []).find((item) => item.user.id === userId) || null
        }

        if (!resolvedConnection && initialRecommendation) {
          resolvedConnection = {
            user: {
              id: userId,
              full_name: initialRecommendation.user_id,
            },
            job_title: null,
            company_id: null,
            company_name: null,
            company_industry: null,
            is_open_to_refer: true,
            hops: null,
            path_via: [],
            skills: [],
          }
        }

        if (!resolvedConnection) {
          throw new Error('Connection not found')
        }

        if (cancelled) return
        setConnection(resolvedConnection)

        // Debug logging
        console.log('Loaded connection:', resolvedConnection)
        console.log('Company ID:', resolvedConnection.company_id)
        console.log('Company name from connection:', resolvedConnection.company_name)

        let companyData = null
        let vacancyData = { vacancies: [] }

        // Try to load company if company_id is available
        if (resolvedConnection.company_id) {
          try {
            const [cData, vData] = await Promise.all([
              api.getCompany(resolvedConnection.company_id),
              me?.id ? api.getRecommendationVacanciesFromTarget(me.id, resolvedConnection.user.id) : Promise.resolve({ vacancies: [] }),
            ])
            companyData = cData
            vacancyData = vData
            console.log('Loaded company:', cData)
          } catch (companyErr) {
            console.error('Failed to load company by ID:', companyErr)
            // Fallback: try to search by company name if available
            if (resolvedConnection.company_name) {
              try {
                const searchResults = await api.searchCompanies(resolvedConnection.company_name, 1)
                if (searchResults && searchResults.length > 0) {
                  companyData = searchResults[0]
                  console.log('Loaded company by name search:', companyData)
                }
              } catch (searchErr) {
                console.error('Failed to search company by name:', searchErr)
              }
            }
          }
        }

        if (cancelled) return
        setCompany(companyData)
        setVacancies(vacancyData.vacancies || [])
      } catch (err) {
        if (!cancelled) {
          console.error('Error loading connection:', err)
          setError(err.message || 'Gagal memuat detail koneksi')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadConnection()

    return () => {
      cancelled = true
    }
  }, [initialConnection, initialRecommendation, me?.id, userId])

  const handleAddConnection = async () => {
    try {
      setAddingConnection(true)
      await api.addConnection(connection.user.id)
      setConnectionAdded(true)
      console.log('Connection added successfully')
    } catch (err) {
      console.error('Failed to add connection:', err)
      alert('Failed to add connection: ' + err.message)
    } finally {
      setAddingConnection(false)
    }
  }

  const companyName = company?.name || connection?.company_name || 'Unknown company'
  const jobTitle = connection?.job_title || 'Connection'
  const recommendationScore = location.state?.recommendation?.score
  const isOpenToRefer = connection?.is_open_to_refer !== false

  const aboutText = useMemo(() => {
    const chunks = []
    if (jobTitle) chunks.push(`${jobTitle} at ${companyName}`)
    if (connection?.hops === 2 && connection?.path_via?.length > 0) {
      chunks.push(`Reachable via ${connection.path_via[0]}`)
    }
    if (connection?.skills?.length > 0) {
      chunks.push(`Skills: ${connection.skills.slice(0, 4).map((skill) => skill.name).join(', ')}`)
    }
    return chunks.length > 0 ? chunks.join('. ') : 'Profile detail for this connection.'
  }, [companyName, connection, jobTitle])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 size={32} className="animate-spin text-slate-300" />
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
          <Link to="/network" className="inline-flex items-center gap-1 mt-3 text-sm font-medium text-red-800 hover:underline">
            <ArrowLeft size={14} /> Kembali ke network
          </Link>
        </div>
      </div>
    )
  }

  if (!connection) return null

  return (
    <div className="space-y-6">
      <Link to="/network" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={16} /> Back to network
      </Link>

      <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="h-24 bg-gradient-to-r from-cyan-700 via-cyan-900 to-slate-900" />
        <div className="px-6 pb-6">
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 -mt-10">
            <div className="flex items-end gap-4">
              <div className="rounded-2xl border-4 border-white shadow-lg">
                <Avatar name={connection.user.full_name} size="lg" />
              </div>
              <div className="pb-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h1 className="text-3xl font-black text-slate-900">{connection.user.full_name}</h1>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${isOpenToRefer ? 'bg-cyan-50 text-cyan-700' : 'bg-slate-100 text-slate-500'}`}>
                    {isOpenToRefer ? 'Open to refer' : 'Referral closed'}
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-500">
                  {[connection.job_title, connection.company_name].filter(Boolean).join(' at ') || 'Network connection'}
                  {connection.hops === 2 && connection.path_via?.length > 0 && (
                    <span className="ml-2 inline-flex items-center gap-1 text-cyan-700">
                      <MapPin size={12} /> via {connection.path_via[0]}
                    </span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {connection.hops === 1 ? (
                // Already connected: show referral options
                <>
                  <button
                    type="button"
                    onClick={() => setReferralOpen(true)}
                    disabled={!company}
                    className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Send size={16} /> Request Referral
                  </button>
                </>
              ) : connectionAdded ? (
                // Connection was just added
                <button
                  disabled
                  className="inline-flex items-center gap-2 rounded-xl bg-emerald-100 px-4 py-2.5 text-sm font-semibold text-emerald-700 cursor-default"
                >
                  <Send size={16} /> Connection Added
                </button>
              ) : (
                // Not connected yet: show add connection button
                <button
                  type="button"
                  onClick={handleAddConnection}
                  disabled={addingConnection}
                  className="inline-flex items-center gap-2 rounded-xl bg-cyan-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-cyan-700 disabled:cursor-wait disabled:opacity-75"
                >
                  {addingConnection ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                  {addingConnection ? 'Adding...' : 'Add Connection'}
                </button>
              )}
              {company && (
                <Link
                  to={`/company/${company.id}`}
                  className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  <Building2 size={16} /> View Company
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-[360px_minmax(0,1fr)] gap-6 items-start">
        <div className="space-y-6">
          <SectionCard title="About" subtitle="Quick summary of this connection">
            <p className="text-sm leading-6 text-slate-600">{aboutText}</p>
            {connection.skills?.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {connection.skills.slice(0, 6).map((skill) => (
                  <span key={skill.id || skill.name} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                    {skill.name}
                  </span>
                ))}
              </div>
            )}
          </SectionCard>

          <SectionCard title="Company Context" subtitle="Current employer details">
            {company ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-50 text-cyan-700 font-bold">
                    {company.name?.[0] || 'C'}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 truncate">{company.name}</p>
                    <p className="text-sm text-slate-500 truncate">{company.industry || 'Industry not set'}</p>
                  </div>
                </div>
                <div className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-medium text-slate-700">Registered employees</span>
                    <span className="inline-flex items-center gap-1 font-semibold text-slate-900">
                      <Users size={14} /> {company.connection_count ?? 0}
                    </span>
                  </div>
                </div>
                <Link
                  to={`/company/${company.id}`}
                  className="inline-flex items-center gap-2 text-sm font-semibold text-cyan-700 hover:underline"
                >
                  Open company page <ArrowLeft size={14} className="rotate-180" />
                </Link>
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-5 text-sm text-slate-500">
                This connection has no declared company yet.
              </div>
            )}
          </SectionCard>
        </div>

        <SectionCard
          title={`Jobs at ${companyName}`}
          subtitle="Active openings available through this connection's company"
          className="lg:min-h-full"
        >
          {vacancies.length > 0 ? (
            <div className="space-y-3">
              <span className="inline-flex rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">
                ACTIVE OPENINGS
              </span>
              {vacancies.slice(0, 4).map((vacancy, index) => (
                <div key={`${vacancy.company_id}-${index}`} className="flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 truncate">{vacancy.description}</p>
                    <p className="text-sm text-slate-500 mt-0.5 truncate">
                      {vacancy.source_url ? 'External source available' : 'Referral opportunity'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {vacancy.source_url && (
                      <a
                        href={vacancy.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
                      >
                        <ExternalLink size={14} /> Source
                      </a>
                    )}
                    {connection.hops === 1 && (
                      <button
                        type="button"
                        onClick={() => setReferralOpen(true)}
                        className="inline-flex items-center gap-1 rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800"
                      >
                        <Briefcase size={14} /> Request Referral
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {company && (
                <div className="pt-3">
                  <Link
                    to={`/company/${company.id}`}
                    className="inline-flex items-center gap-1 text-sm font-semibold text-cyan-700 hover:underline"
                  >
                    View all openings at {company.name} <ArrowLeft size={14} className="rotate-180" />
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
              No openings were found for this connection's company.
            </div>
          )}
        </SectionCard>
      </div>

      <ReferralRequestModal
        open={referralOpen}
        company={company}
        connection={connection}
        onClose={() => setReferralOpen(false)}
        onSuccess={() => {
          setReferralOpen(false)
        }}
      />
    </div>
  )
}
