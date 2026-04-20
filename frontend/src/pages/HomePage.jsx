import { Search, Users, Send, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Selamat datang di Referly</h1>
        <p className="text-gray-500 mt-1">Temukan siapa yang kamu kenal di perusahaan impianmu.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {[{to:'/search',icon:Search,title:'Cari Perusahaan',desc:'Lihat koneksimu di perusahaan target',color:'bg-blue-50 text-blue-600'},
          {to:'/profile',icon:Users,title:'Sinkronkan Kontak',desc:'Hubungkan buku kontakmu',color:'bg-green-50 text-green-600'},
          {to:'/referrals',icon:Send,title:'Referral Saya',desc:'Lihat status permintaan referral',color:'bg-purple-50 text-purple-600'}
        ].map(({to,icon:Icon,title,desc,color})=>(
          <Link key={to} to={to} className="bg-white rounded-xl border border-surface-200 p-5 hover:shadow-md transition-shadow group">
            <div className={`w-10 h-10 rounded-lg ${color} flex items-center justify-center mb-3`}><Icon size={20}/></div>
            <h3 className="font-semibold text-gray-900 flex items-center gap-1">{title}<ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity"/></h3>
            <p className="text-sm text-gray-500 mt-1">{desc}</p>
          </Link>
        ))}
      </div>
      <div className="bg-white rounded-xl border border-surface-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Ringkasan Jaringanmu</h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          {[{v:'--',l:'Koneksi'},{v:'--',l:'Perusahaan'},{v:'--',l:'Referral Terkirim'}].map(({v,l})=>(
            <div key={l}><p className="text-3xl font-bold text-primary-600">{v}</p><p className="text-sm text-gray-500">{l}</p></div>
          ))}
        </div>
      </div>
    </div>
  )
}