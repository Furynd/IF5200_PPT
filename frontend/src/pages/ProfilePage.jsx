import { useEffect, useState } from 'react'
import { User, Briefcase, Phone } from 'lucide-react'
import { api } from '../lib/api'

export default function ProfilePage() {
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    api.me()
      .then((data) => {
        if (active) setProfile(data)
      })
      .catch((err) => {
        if (active) setError(err.message)
      })

    return () => {
      active = false
    }
  }, [])

  const user = profile?.user ?? profile ?? null
  const phoneNumber = user?.phone_number || user?.phoneNumber || user?.phone || '+628xxxxxxxxxx'

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Profil Saya</h1>
      <div className="bg-white rounded-xl border border-surface-200 p-6 space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center"><User size={32} className="text-primary-600"/></div>
          <div>
            <h2 className="text-lg font-semibold">{user?.full_name || 'Nama Pengguna'}</h2>
            <p className="text-gray-500">{user?.email || 'email@example.com'}</p>
            {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
          </div>
        </div>
        <hr className="border-surface-200"/>
        <div className="space-y-3">
          {[
            { icon: Briefcase, label: 'Perusahaan', value: 'Belum dideklarasikan' },
            { icon: Phone, label: 'Telepon', value: phoneNumber },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} className="flex items-center gap-3">
              <Icon size={18} className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">{label}</p>
                <p className="font-medium">{value}</p>
              </div>
            </div>
          ))}
        </div>
        <button className="w-full py-2.5 border-2 border-dashed border-primary-200 text-primary-600 rounded-lg font-medium hover:bg-primary-50">Sinkronkan Kontak Telepon</button>
      </div>
    </div>
  )
}