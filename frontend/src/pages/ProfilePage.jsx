import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Upload, FileText, X, Pencil, Share2, Eye, Trash2, Check } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { api } from '../lib/api'
import CompanyCombobox from '../components/CompanyCombobox'
import ContactSyncModal from '../components/ContactSyncModal'

export default function ProfilePage() {
  const { user, setUser } = useAuth()
  const [searchParams] = useSearchParams()
  const showWelcome = searchParams.get('welcome') === '1'

  const [editing, setEditing] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [jobTitle, setJobTitle] = useState('')
  const [shortBio, setShortBio] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [syncModalOpen, setSyncModalOpen] = useState(false)

  const [cv, setCv] = useState(null)
  const [recentUploads, setRecentUploads] = useState([])
  const [cvLoading, setCvLoading] = useState(true)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (user?.company) {
      setSelectedCompany(user.company)
      setJobTitle(user.job_title || '')
      setShortBio(user.short_bio || '')
    }
  }, [user])

  // Fetch existing CV from backend — gracefully handles 404/errors
  useEffect(() => {
    setCvLoading(true)
    api.getUserCV()
      .then(data => {
        if (data?.filename) {
          setRecentUploads([{
            name: data.filename,
            size: data.size_mb ? `${data.size_mb} MB` : '',
            uploaded: data.uploaded_at ? new Date(data.uploaded_at).toLocaleDateString() : 'Previously uploaded',
          }])
        }
      })
      .catch(() => {})
      .finally(() => setCvLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setError('')
    try {
      const updated = await api.updateProfile({
        company_id: selectedCompany?.id || null,
        job_title: jobTitle.trim() || null,
      })
      setUser(updated)
      setEditing(false)
    } catch (err) {
      setError(err.message || 'Failed to save.')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setSelectedCompany(user?.company || null)
    setJobTitle(user?.job_title || '')
    setShortBio(user?.short_bio || '')
    setEditing(false)
    setError('')
  }

  const handleCvChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const allowed = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowed.includes(file.type)) { setError('CV must be PDF or Word (.doc/.docx)'); return }
    if (file.size > 5 * 1024 * 1024) { setError('CV must be under 5 MB'); return }
    setError('')
    setCv(file)
    const entry = {
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      uploaded: 'Just now',
    }
    setRecentUploads(prev => [entry, ...prev.slice(0, 2)])
    // Extract skills from CV in the background
    api.extractSkillsFromPDF(file).catch(() => {})
    e.target.value = ''
  }

  if (!user) return null

  const initials = user.full_name?.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?'
  const displayRole = [user.job_title, user.company?.name].filter(Boolean).join(' at ')

  return (
    <div className="max-w-2xl space-y-6">
      {showWelcome && !user.company && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="font-semibold text-blue-900">Welcome, {user.full_name?.split(' ')[0]}!</p>
          <p className="text-sm text-blue-700 mt-0.5">
            Complete your profile to start networking and finding referrals.
          </p>
        </div>
      )}

      {/* Profile header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-slate-900 text-white flex items-center justify-center text-2xl font-bold">
                {initials}
              </div>
              <button className="absolute bottom-0 right-0 w-6 h-6 rounded-full bg-white border border-gray-200 flex items-center justify-center shadow-sm hover:bg-gray-50">
                <Pencil size={12} className="text-gray-600" />
              </button>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">{user.full_name}</h1>
              <p className="text-gray-500 text-sm mt-0.5">{displayRole || 'Add your role and company'}</p>
            </div>
          </div>
          <button
            onClick={() => setSyncModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-gray-50 transition-colors"
          >
            <Share2 size={15} />
            Share Profile
          </button>
        </div>
      </div>

      {/* Personal Information */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-semibold text-slate-900 flex items-center gap-2">
            <span className="text-base">👤</span> Personal Information
          </h2>
          {!editing ? (
            <button
              onClick={() => setEditing(true)}
              className="text-sm font-medium text-slate-600 hover:text-slate-900 flex items-center gap-1.5"
            >
              <Pencil size={13} /> Edit All
            </button>
          ) : (
            <div className="flex gap-2">
              <button onClick={handleSave} disabled={saving}
                className="flex items-center gap-1.5 text-sm font-medium px-3 py-1.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-50 transition-colors">
                <Check size={13} /> {saving ? 'Saving...' : 'Save'}
              </button>
              <button onClick={handleCancel} disabled={saving}
                className="flex items-center gap-1.5 text-sm font-medium px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors">
                <X size={13} /> Cancel
              </button>
            </div>
          )}
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <Field label="Full Name" value={user.full_name} editing={false} />
          <Field label="Email Address" value={user.email} editing={false} />
          <Field label="Phone Number" value={user.phone_number} editing={false} />
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Current Role</label>
            {editing ? (
              <input
                type="text"
                value={jobTitle}
                onChange={e => setJobTitle(e.target.value)}
                placeholder="e.g. Senior Product Designer"
                className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:bg-white"
              />
            ) : (
              <div className="px-3 py-2.5 bg-gray-50 rounded-lg text-sm text-slate-700 border border-transparent">
                {user.job_title || <span className="text-gray-400 italic">Not set</span>}
              </div>
            )}
          </div>
        </div>

        {/* Company */}
        <div className="mt-4">
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Company</label>
          {editing ? (
            <CompanyCombobox value={selectedCompany} onChange={setSelectedCompany} disabled={saving} />
          ) : (
            <div className="px-3 py-2.5 bg-gray-50 rounded-lg text-sm text-slate-700 border border-transparent">
              {user.company?.name || <span className="text-gray-400 italic">Not declared</span>}
            </div>
          )}
        </div>

        {/* Short bio */}
        <div className="mt-4 sm:col-span-2">
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Short Bio</label>
          {editing ? (
            <textarea
              value={shortBio}
              onChange={e => setShortBio(e.target.value)}
              rows={3}
              placeholder="Strategic designer focused on building scalable financial tools..."
              className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:bg-white resize-none"
            />
          ) : (
            <div className="px-3 py-2.5 bg-gray-50 rounded-lg text-sm text-slate-700 border border-transparent min-h-[60px]">
              {user.short_bio || shortBio || <span className="text-gray-400 italic">Add a short bio</span>}
            </div>
          )}
        </div>

        {error && (
          <div className="mt-3 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">{error}</div>
        )}
      </div>

      {/* Curriculum Vitae */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-slate-900 flex items-center gap-2 mb-5">
          <FileText size={16} className="text-gray-500" /> Curriculum Vitae
        </h2>

        {/* Upload area */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleCvChange}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center gap-3 hover:border-slate-400 hover:bg-gray-50 transition-colors group"
        >
          <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center group-hover:bg-blue-100 transition-colors">
            <Upload size={20} className="text-blue-500" />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-slate-700">Click to upload or drag and drop</p>
            <p className="text-xs text-gray-400 mt-0.5">PDF, DOCX (Max 5MB)</p>
          </div>
          <div className="px-4 py-2 bg-slate-900 text-white text-sm font-semibold rounded-lg group-hover:bg-slate-800 transition-colors">
            Browse Files
          </div>
        </button>

        {cvLoading && (
          <div className="mt-4 h-12 bg-gray-100 rounded-lg animate-pulse" />
        )}

        {/* Recent uploads */}
        {!cvLoading && recentUploads.length > 0 && (
          <div className="mt-5">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Recent Uploads</p>
            <div className="space-y-2">
              {recentUploads.map((upload, i) => (
                <div key={i} className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg">
                  <div className="w-8 h-8 rounded bg-red-50 flex items-center justify-center flex-shrink-0">
                    <FileText size={16} className="text-red-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-700 truncate">{upload.name}</p>
                    <p className="text-xs text-gray-400">{upload.uploaded} · {upload.size}</p>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <button className="p-1.5 text-gray-400 hover:text-slate-700 transition-colors" title="Preview">
                      <Eye size={15} />
                    </button>
                    <button
                      onClick={() => setRecentUploads(prev => prev.filter((_, j) => j !== i))}
                      className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <ContactSyncModal
        open={syncModalOpen}
        onClose={() => setSyncModalOpen(false)}
        onSuccess={() => setSyncModalOpen(false)}
      />
    </div>
  )
}

function Field({ label, value, editing, onChange, placeholder }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">{label}</label>
      {editing ? (
        <input
          type="text"
          value={value || ''}
          onChange={onChange}
          placeholder={placeholder}
          className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-300 focus:bg-white"
        />
      ) : (
        <div className="px-3 py-2.5 bg-gray-50 rounded-lg text-sm text-slate-700 border border-transparent">
          {value || <span className="text-gray-400 italic">Not set</span>}
        </div>
      )}
    </div>
  )
}
