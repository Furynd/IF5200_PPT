import { useParams } from 'react-router-dom'
import { Building2, Users } from 'lucide-react'

export default function CompanyPage() {
  const { id } = useParams()
  // TODO: integrate with api.getCompany(id) + api.getConnectionsAtCompany(id) in Week 4-5
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-surface-200 p-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-primary-50 flex items-center justify-center"><Building2 size={28} className="text-primary-600"/></div>
          <div><h1 className="text-xl font-bold text-gray-900">Nama Perusahaan</h1><p className="text-gray-500">Technology</p><p className="text-sm text-gray-400 mt-1">ID: {id}</p></div>
        </div>
      </div>
      <div className="bg-white rounded-xl border border-surface-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><Users size={18}/>Koneksimu di Perusahaan Ini</h2>
        <p className="text-gray-500 text-sm">Belum ada data. Sinkronkan kontak terlebih dahulu.</p>
      </div>
    </div>
  )
}