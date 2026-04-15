import { Shield, Bell } from 'lucide-react'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Pengaturan</h1>
      <div className="bg-white rounded-xl border border-surface-200 p-6 space-y-6">
        <div>
          <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-4"><Shield size={18}/>Privasi Referral</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div><p className="font-medium text-gray-900">Terbuka untuk referral</p><p className="text-sm text-gray-500">Izinkan koneksi mengirim permintaan referral</p></div>
              <button className="w-12 h-6 bg-primary-600 rounded-full relative"><span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow"/></button>
            </div>
            <div><label className="text-sm font-medium text-gray-700">Kuota per bulan</label>
            <input type="number" defaultValue={10} min={1} max={50} className="mt-1 w-24 px-3 py-2 border border-surface-200 rounded-lg text-center"/></div>
          </div>
        </div>
        <hr className="border-surface-200"/>
        <div><h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-4"><Bell size={18}/>Notifikasi</h2>
        <p className="text-sm text-gray-500">Pengaturan notifikasi akan tersedia segera.</p></div>
      </div>
    </div>
  )
}