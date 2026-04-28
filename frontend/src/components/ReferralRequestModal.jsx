import { useState } from 'react'
import { X, Loader2, Send } from 'lucide-react'
import { api } from '../lib/api'

export default function ReferralRequestModal({ open, company, connection, onClose, onSuccess }) {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!open || !company || !connection) return null

  const reset = () => {
    setMessage('')
    setLoading(false)
    setError('')
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    const formData = new FormData()
    formData.append('company_id', company.id)
    formData.append('referee_user_id', connection.user.id)
    formData.append('message', message.trim())

    try {
      setLoading(true)
      const result = await api.sendReferral(formData)
      reset()
      onSuccess?.(result)
      onClose()
    } catch (err) {
      setError(err.message || 'Gagal mengirim referral.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 px-4">
      <div className="w-full max-w-xl rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Kirim Referral</p>
            <h3 className="text-lg font-bold text-slate-900 mt-1">{company.name}</h3>
            <p className="text-sm text-slate-500">
              Tujuan: {connection.user.full_name}
            </p>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="rounded-full p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 px-5 py-5">
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
            {connection.is_open_to_refer
              ? 'Koneksi ini terbuka untuk referral. Pesan akan dikirim via Fonnte free menggunakan CV dari profil kamu.'
              : 'Koneksi ini tidak sedang membuka referral.'}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700">Pesan tambahan</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
              placeholder="Tambahkan konteks singkat untuk koneksimu..."
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-300"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-1">
            <button
              type="button"
              onClick={handleClose}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              {loading ? 'Mengirim...' : 'Kirim Referral'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
