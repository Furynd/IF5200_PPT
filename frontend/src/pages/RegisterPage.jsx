import { useState, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Upload, FileText, X } from 'lucide-react'
import { useAuth } from '../lib/auth'

// Normalize Indonesian phone numbers to E.164 format (+62...)
function normalizePhone(raw) {
  const digits = raw.replace(/\D/g, '')
  if (digits.startsWith('62')) return '+' + digits
  if (digits.startsWith('0')) return '+62' + digits.slice(1)
  if (digits.startsWith('8')) return '+62' + digits
  return '+' + digits
}

export default function RegisterPage() {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    password_confirm: '',
    phone_number: ''
  })
  const [cv, setCv] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()
  const fileInputRef = useRef(null)

  const handleCvChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const allowed = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowed.includes(file.type)) {
      setError('CV harus berformat PDF atau Word (.doc / .docx)')
      e.target.value = ''
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('Ukuran CV maksimal 5 MB')
      e.target.value = ''
      return
    }
    setError('')
    setCv(file)
  }

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const validate = () => {
    if (form.full_name.trim().length < 2) return 'Nama lengkap minimal 2 karakter'
    if (!/^\S+@\S+\.\S+$/.test(form.email)) return 'Format email tidak valid'
    if (form.password.length < 8) return 'Password minimal 8 karakter'
    if (form.password !== form.password_confirm) return 'Konfirmasi password tidak cocok'
    const phone = normalizePhone(form.phone_number)
    if (!/^\+62[0-9]{9,13}$/.test(phone)) return 'Format nomor telepon tidak valid (contoh: 08123456789)'
    if (!cv) return 'CV wajib diunggah'
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)
    try {
      await register({
        full_name: form.full_name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        phone_number: normalizePhone(form.phone_number),
      })
      // After registration, send user to profile to complete company declaration
      navigate('/profile?welcome=1', { replace: true })
    } catch (err) {
      setError(err.message || 'Gagal mendaftar. Silakan coba lagi.')
    } finally {
      setLoading(false)
    }
  }

  const fields = [
    { label: 'Nama Lengkap', field: 'full_name', type: 'text', autoComplete: 'name' },
    { label: 'Email', field: 'email', type: 'email', autoComplete: 'email' },
    { label: 'Nomor Telepon', field: 'phone_number', type: 'tel', autoComplete: 'tel', placeholder: '08123456789' },
    { label: 'Password', field: 'password', type: 'password', autoComplete: 'new-password', hint: 'Minimal 8 karakter' },
    { label: 'Konfirmasi Password', field: 'password_confirm', type: 'password', autoComplete: 'new-password' },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 px-4 py-8">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center text-primary-600 mb-2">Daftar Referly</h1>
        <p className="text-center text-gray-500 mb-8">Buat akun untuk mulai mencari koneksi</p>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-surface-200 p-6 space-y-4">
          {fields.map(({ label, field, type, autoComplete, placeholder, hint }) => (
            <div key={field}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                type={type}
                value={form[field]}
                onChange={update(field)}
                required
                autoComplete={autoComplete}
                placeholder={placeholder || ''}
                disabled={loading}
                className="w-full px-3 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
              />
              {hint && <p className="text-xs text-gray-400 mt-1">{hint}</p>}
            </div>
          ))}

          {/* CV Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CV <span className="text-red-500">*</span>
              <span className="text-gray-400 font-normal ml-1">(PDF atau Word, maks. 5 MB)</span>
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleCvChange}
              disabled={loading}
              className="hidden"
            />
            {cv ? (
              <div className="flex items-center gap-2 px-3 py-2 border border-primary-300 bg-primary-50 rounded-lg">
                <FileText size={16} className="text-primary-600 flex-shrink-0" />
                <span className="text-sm text-primary-700 truncate flex-1">{cv.name}</span>
                <button
                  type="button"
                  onClick={() => { setCv(null); fileInputRef.current.value = '' }}
                  className="text-gray-400 hover:text-red-500 flex-shrink-0"
                >
                  <X size={15} />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => fileInputRef.current.click()}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 border border-dashed border-surface-200 rounded-lg text-sm text-gray-500 hover:border-primary-400 hover:text-primary-600 transition-colors disabled:opacity-50"
              >
                <Upload size={16} />
                Unggah CV
              </button>
            )}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Mendaftar...' : 'Daftar'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Sudah punya akun?{' '}
          <Link to="/login" className="text-primary-600 font-medium hover:underline">Masuk</Link>
        </p>
      </div>
    </div>
  )
}
