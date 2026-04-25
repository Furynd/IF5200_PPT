import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Search, ChevronRight, Briefcase } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { api } from '../lib/api'
import CompanyCombobox from '../components/CompanyCombobox'

function normalizePhone(raw) {
  const digits = raw.replace(/\D/g, '')
  if (digits.startsWith('62')) return '+' + digits
  if (digits.startsWith('0')) return '+62' + digits.slice(1)
  if (digits.startsWith('8')) return '+62' + digits
  return '+' + digits
}

function PublicNavbar() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <span className="font-bold text-slate-900 text-xl">Referly</span>
        <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
          <a href="#" className="hover:text-slate-900">Home</a>
          <a href="#" className="hover:text-slate-900">About</a>
          <Link to="/register" className="font-semibold text-slate-900 border-b-2 border-slate-900 pb-0.5">Registration</Link>
        </nav>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-slate-900">Login</Link>
          <Link to="/register" className="text-sm font-medium bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors">Sign Up</Link>
        </div>
      </div>
    </header>
  )
}

function PublicFooter() {
  return (
    <footer className="bg-white border-t border-gray-200 py-6">
      <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="font-bold text-slate-900">Referly</span>
          <p className="text-xs text-gray-400 mt-0.5">© 2026 Referly. All rights reserved.</p>
        </div>
        <div className="flex gap-6 text-xs text-gray-500">
          <a href="#" className="hover:text-slate-700">Privacy Policy</a>
          <a href="#" className="hover:text-slate-700">Terms of Service</a>
          <a href="#" className="hover:text-slate-700">Contact</a>
        </div>
      </div>
    </footer>
  )
}

export default function RegisterPage() {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({ full_name: '', email: '', password: '', phone_number: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [employmentStatus, setEmploymentStatus] = useState('')
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const validateStep1 = () => {
    if (form.full_name.trim().length < 2) return 'Full name must be at least 2 characters'
    if (!/^\S+@\S+\.\S+$/.test(form.email)) return 'Invalid email format'
    if (form.password.length < 8) return 'Password must be at least 8 characters'
    const phone = normalizePhone(form.phone_number)
    if (!/^\+62[0-9]{9,13}$/.test(phone)) return 'Enter a valid Indonesian phone number (e.g. 08123456789)'
    return null
  }

  const handleStep1Submit = (e) => {
    e.preventDefault()
    const err = validateStep1()
    if (err) { setError(err); return }
    setError('')
    setStep(2)
  }

  const handleStep2Continue = () => {
    if (!employmentStatus) { setError('Please select your employment status'); return }
    setError('')
    if (employmentStatus === 'searching') {
      handleFinalSubmit(null)
    } else {
      setStep(3)
    }
  }

  const handleFinalSubmit = async (companyId) => {
    setLoading(true)
    setError('')
    try {
      await register({
        full_name: form.full_name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        phone_number: normalizePhone(form.phone_number),
      })
      if (companyId) {
        await api.updateProfile({ company_id: companyId })
      }
      navigate('/profile?welcome=1', { replace: true })
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
      setStep(1)
    } finally {
      setLoading(false)
    }
  }

  const handleStep3Submit = () => {
    if (!selectedCompany) { setError('Please search and select your company'); return }
    handleFinalSubmit(selectedCompany.id)
  }

  /* ── Step 1: Create Account ─────────────────────────────────────────── */
  if (step === 1) return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <PublicNavbar />
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-4xl bg-white rounded-2xl shadow-sm overflow-hidden flex min-h-[540px]">
          {/* Left dark panel */}
          <div className="hidden md:flex w-2/5 bg-slate-900 flex-col justify-end p-8 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-slate-800/60 to-slate-900" />
            <div className="relative z-10">
              <h2 className="text-2xl font-bold text-white leading-snug">
                Elevate your career through trusted connections.
              </h2>
              <p className="text-slate-400 mt-3 text-sm leading-relaxed">
                Join Referly to access exclusive opportunities or help others grow in your network.
              </p>
            </div>
          </div>

          {/* Right form */}
          <div className="flex-1 p-8 md:p-10 flex flex-col justify-center">
            <h1 className="text-2xl font-bold text-slate-900 mb-1">Create Account</h1>
            <p className="text-sm text-gray-500 mb-6">Join the premium referral ecosystem.</p>

            <div className="space-y-3 mb-5">
              <button className="w-full flex items-center justify-center gap-3 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-gray-50 transition-colors">
                <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Continue with Google
              </button>
              <button className="w-full flex items-center justify-center gap-3 px-4 py-2.5 border border-[#0077b5] text-[#0077b5] rounded-lg text-sm font-medium hover:bg-blue-50 transition-colors">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
                Continue with LinkedIn
              </button>
            </div>

            <div className="relative my-4">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-200" /></div>
              <div className="relative flex justify-center"><span className="bg-white px-3 text-xs text-gray-400">OR WITH EMAIL</span></div>
            </div>

            <form onSubmit={handleStep1Submit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wide">Full Name</label>
                <input type="text" value={form.full_name} onChange={update('full_name')} required placeholder="Alex Sterling"
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:bg-white" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wide">Work Email</label>
                <input type="email" value={form.email} onChange={update('email')} required placeholder="alex@company.com"
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:bg-white" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wide">Password</label>
                <div className="relative">
                  <input type={showPassword ? 'text' : 'password'} value={form.password} onChange={update('password')} required
                    placeholder="Min. 8 characters"
                    className="w-full px-3 py-2.5 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:bg-white" />
                  <button type="button" onClick={() => setShowPassword(v => !v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wide">Phone Number</label>
                <input type="tel" value={form.phone_number} onChange={update('phone_number')} required placeholder="08123456789"
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:bg-white" />
              </div>

              {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">{error}</div>}

              <button type="submit"
                className="w-full py-2.5 bg-slate-900 text-white rounded-lg font-semibold hover:bg-slate-800 transition-colors">
                Complete Registration
              </button>
            </form>

            <p className="text-center text-xs text-gray-400 mt-3">
              By signing up, you agree to Referly's{' '}
              <a href="#" className="underline text-gray-600">Terms</a> and{' '}
              <a href="#" className="underline text-gray-600">Privacy Policy</a>.
            </p>
          </div>
        </div>
      </div>
      <PublicFooter />
    </div>
  )

  /* ── Step 2: Employment Status ──────────────────────────────────────── */
  if (step === 2) return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <PublicNavbar />
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">
          <div className="mb-6">
            <span className="inline-block text-xs font-semibold text-slate-600 bg-gray-200 px-3 py-1 rounded-full uppercase tracking-widest">
              Step 02
            </span>
            <h1 className="text-3xl font-bold text-slate-900 mt-3">Registration - Step 02</h1>
            <p className="text-gray-500 mt-2">
              Help us personalize your experience by defining your current professional standing.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h2 className="font-semibold text-slate-900 mb-1">Employment Status</h2>
            <p className="text-sm text-gray-500 mb-5">Choose the option that best describes your situation.</p>

            <div className="space-y-3 mb-5">
              <button
                onClick={() => { setEmploymentStatus('searching'); setError('') }}
                className={`w-full flex items-start gap-4 p-4 rounded-xl border-2 text-left transition-colors ${
                  employmentStatus === 'searching' ? 'border-slate-900 bg-slate-50' : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Search size={18} className="text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-slate-900">I am searching</p>
                  <p className="text-sm text-gray-500 mt-0.5">
                    Register as a Pelamar to find and request referral opportunities. Access our digital network of curators.
                  </p>
                </div>
                <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 transition-colors ${
                  employmentStatus === 'searching' ? 'border-slate-900 bg-slate-900' : 'border-gray-300'
                }`} />
              </button>

              <button
                onClick={() => { setEmploymentStatus('employed'); setError('') }}
                className={`w-full flex items-start gap-4 p-4 rounded-xl border-2 text-left transition-colors ${
                  employmentStatus === 'employed' ? 'border-slate-900 bg-slate-50' : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Briefcase size={18} className="text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-slate-900">I am employed</p>
                  <p className="text-sm text-gray-500 mt-0.5">
                    <span className="font-semibold text-slate-600">Required:</span> Company Verification step will follow after selection. Share opportunities with your network.
                  </p>
                </div>
                <div className={`w-5 h-5 rounded-full border-2 flex-shrink-0 mt-0.5 transition-colors ${
                  employmentStatus === 'employed' ? 'border-slate-900 bg-slate-900' : 'border-gray-300'
                }`} />
              </button>
            </div>

            {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg mb-4">{error}</div>}

            <button
              onClick={handleStep2Continue}
              disabled={loading}
              className="w-full py-2.5 bg-slate-900 text-white rounded-lg font-semibold hover:bg-slate-800 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Registering...' : 'Continue'}
            </button>
          </div>

          <div className="mt-6 flex items-center gap-3">
            <div className="flex -space-x-2">
              {['bg-blue-400', 'bg-emerald-400', 'bg-purple-400'].map((c, i) => (
                <div key={i} className={`w-8 h-8 rounded-full ${c} border-2 border-white`} />
              ))}
            </div>
            <p className="text-sm text-gray-500">
              Join 12,000+ professionals currently navigating their careers through Referly's curated networks.
            </p>
          </div>
        </div>
      </div>
      <PublicFooter />
    </div>
  )

  /* ── Step 3: Employment Verification ────────────────────────────────── */
  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <PublicNavbar />
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">
          <div className="flex items-center gap-2 text-xs text-gray-400 font-semibold uppercase tracking-wider mb-6">
            <span className="text-gray-600">Step 03</span>
            <span>—</span>
            <span className="text-gray-600">Verification</span>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 p-8">
            <h1 className="text-2xl font-bold text-slate-900 mb-1">Employment Verification</h1>
            <p className="text-sm text-gray-500 mb-6">
              Search for your organization to begin the verification process. We ensure high-trust connections by validating professional identities.
            </p>

            <div className="mb-6">
              <label className="block text-xs font-semibold text-slate-700 mb-2 uppercase tracking-wide">Company Name</label>
              <CompanyCombobox value={selectedCompany} onChange={setSelectedCompany} />
              <button type="button" className="text-sm text-slate-500 hover:text-slate-700 mt-2">
                Can't find your company? Add it here →
              </button>
            </div>

            {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg mb-4">{error}</div>}

            <button
              onClick={handleStep3Submit}
              disabled={loading}
              className="w-full py-2.5 bg-slate-900 text-white rounded-lg font-semibold hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2 transition-colors"
            >
              {loading ? 'Completing registration...' : <>Complete Registration <ChevronRight size={16} /></>}
            </button>
          </div>

          <div className="flex justify-center gap-2 mt-6">
            {[1, 2, 3].map(i => (
              <div key={i} className={`h-2 rounded-full transition-all ${i === 3 ? 'w-8 bg-slate-900' : 'w-4 bg-gray-300'}`} />
            ))}
          </div>
        </div>
      </div>
      <PublicFooter />
    </div>
  )
}
