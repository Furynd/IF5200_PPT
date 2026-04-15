import { Send, Inbox } from 'lucide-react'

export default function ReferralsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Referral Saya</h1>
      <div className="flex gap-2">
        <button className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium flex items-center gap-2"><Send size={16}/>Terkirim</button>
        <button className="px-4 py-2 bg-white border border-surface-200 text-gray-600 rounded-lg text-sm font-medium flex items-center gap-2 hover:bg-surface-50"><Inbox size={16}/>Diterima</button>
      </div>
      <div className="bg-white rounded-xl border border-surface-200 p-8 text-center">
        <Send size={40} className="mx-auto text-gray-300 mb-3"/>
        <p className="text-gray-500">Belum ada permintaan referral.</p>
        <p className="text-sm text-gray-400 mt-1">Cari perusahaan dan minta referral dari koneksimu.</p>
      </div>
    </div>
  )
}