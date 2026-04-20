import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export default function RegisterPage() {
  const [form, setForm] = useState({ full_name: '', email: '', password: '', phone_number: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const update = (f) => (e) => setForm({ ...form, [f]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError('')
    try { await api.register(form); navigate('/login') }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center text-primary-600 mb-2">Daftar Referly</h1>
        <p className="text-center text-gray-500 mb-8">Buat akun untuk mulai mencari koneksi</p>
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-surface-200 p-6 space-y-4">
          {[{l:'Nama Lengkap',f:'full_name',t:'text'},{l:'Email',f:'email',t:'email'},{l:'Nomor Telepon',f:'phone_number',t:'tel'},{l:'Password',f:'password',t:'password'}].map(({l,f,t})=>(
            <div key={f}><label className="block text-sm font-medium text-gray-700 mb-1">{l}</label>
            <input type={t} value={form[f]} onChange={update(f)} required className="w-full px-3 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
          ))}
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="w-full py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">{loading ? 'Mendaftar...' : 'Daftar'}</button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">Sudah punya akun? <Link to="/login" className="text-primary-600 font-medium hover:underline">Masuk</Link></p>
      </div>
    </div>
  )
}