import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { User, Briefcase, Phone, Check, X, Users } from 'lucide-react'
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
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [syncModalOpen, setSyncModalOpen] = useState(false)
  const [stats, setStats] = useState({ connections: 0, companies: 0 })

  useEffect(() => {
    if (user?.company) {
      setSelectedCompany(user.company)
      setJobTitle(user.job_title || '')
    }
    // Fetch network stats
    api.getNetworkStats?.()
      .then(data => setStats(data))
      .catch(() => {})
  }, [user])

  const handleSave = async () => {
    if (!selectedCompany) {
      setError('Silakan pilih perusahaan terlebih dahulu')
      return
    }
    setSaving(true)
    setError('')
    try {
      const updated = await api.updateProfile({
        company_id: selectedCompany.id,
        job_title: jobTitle.trim() || null,
      })
      setUser(updated)
      setEditing(false)
    } catch (err) {
      setError(err.message || 'Gagal menyimpan.')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setSelectedCompany(user?.company || null)
    setJobTitle(user?.job_title || '')
    setEditing(false)
    setError('')
  }

  const handleSyncSuccess = (result) => {
    // Refresh stats after successful sync
    setStats(prev => ({
      ...prev,
      connections: prev.connections + result.connections_created,
    }))
  }

  if (!user) return null

  return (
    <div className="space-y-6">
      {showWelcome && !user.company && (
        <div className="bg-primary-50 border border-primary-200 rounded-xl p-4">
          <p className="font-medium text-primary-900">Selamat datang, {user.full_name.split(' ')[0]}! 👋</p>
          <p className="text-sm text-primary-700 mt-1">
            Deklarasikan perusahaanmu dan sinkronkan kontak agar koneksi bisa menemukanmu.
          </p>
        </div>
      )}

      <h1 className="text-2xl font-bold">Profil Saya</h1>

      <div className="bg-white rounded-xl border border-surface-200 p-6 space-y-4">
        {/* User header */}
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center">
            <User size={32} className="text-primary-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">{user.full_name}</h2>
            <p className="text-gray-500">{user.email}</p>
          </div>
        </div>

        {/* Network stats */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <StatCard
            icon={Users}
            label="Koneksi"
            value={stats.connections}
          />
          <StatCard
            icon={Briefcase}
            label="Perusahaan"
            value={stats.companies}
          />
        </div>

        <hr className="border-surface-200" />

        {/* Company declaration */}
        <div className="flex items-start gap-3">
          <Briefcase size={18} className="text-gray-400 mt-1 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-gray-500">Perusahaan</p>
            {editing ? (
              <div className="mt-2 space-y-3">
                <CompanyCombobox value={selectedCompany} onChange={setSelectedCompany} disabled={saving} />
                <input
                  type="text"
                  value={jobTitle}
                  onChange={e => setJobTitle(e.target.value)}
                  placeholder="Jabatan (opsional)"
                  disabled={saving}
                  className="w-full px-3 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
                />
              </div>
            ) : (
              <div>
                <p className="font-medium">
                  {user.company?.name || <span className="text-gray-400 italic">Belum dideklarasikan</span>}
                </p>
                {user.job_title && <p className="text-sm text-gray-500">{user.job_title}</p>}
              </div>
            )}
          </div>
        </div>

        {/* Phone */}
        <div className="flex items-center gap-3">
          <Phone size={18} className="text-gray-400" />
          <div>
            <p className="text-sm text-gray-500">Telepon</p>
            <p className="font-medium">{user.phone_number}</p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">{error}</div>
        )}

        {/* Action buttons */}
        {editing ? (
          <div className="flex gap-2 pt-2">
            <button onClick={handleSave} disabled={saving}
              className="flex-1 py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center gap-2">
              <Check size={16} />{saving ? 'Menyimpan...' : 'Simpan'}
            </button>
            <button onClick={handleCancel} disabled={saving}
              className="px-4 py-2.5 border border-surface-200 rounded-lg font-medium hover:bg-surface-50 disabled:opacity-50 flex items-center justify-center gap-2">
              <X size={16} />Batal
            </button>
          </div>
        ) : (
          <div className="space-y-2 pt-2">
            <button onClick={() => setEditing(true)}
              className="w-full py-2.5 border-2 border-dashed border-primary-200 text-primary-600 rounded-lg font-medium hover:bg-primary-50">
              {user.company ? 'Ubah Perusahaan' : 'Deklarasikan Perusahaan'}
            </button>
            <button onClick={() => setSyncModalOpen(true)}
              className="w-full py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 flex items-center justify-center gap-2">
              <Users size={16} />
              Sinkronkan Kontak Telepon
            </button>
          </div>
        )}
      </div>

      <ContactSyncModal
        open={syncModalOpen}
        onClose={() => setSyncModalOpen(false)}
        onSuccess={handleSyncSuccess}
      />
    </div>
  )
}

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="bg-surface-50 rounded-lg p-3 flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg bg-white flex items-center justify-center">
        <Icon size={18} className="text-primary-600" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900 leading-none">{value}</p>
        <p className="text-xs text-gray-500 mt-1">{label}</p>
      </div>
    </div>
  )
}
