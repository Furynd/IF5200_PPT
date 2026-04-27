import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle, Users, Zap, Shield } from 'lucide-react'
import PublicNavbar from '../components/PublicNavbar'
import PublicFooter from '../components/PublicFooter'

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <PublicNavbar />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <h1 className="text-5xl font-bold text-slate-900 leading-tight">
            The Power of<br />
            <span className="text-slate-700">Referrals.</span>
          </h1>
          <p className="text-gray-500 mt-5 text-lg leading-relaxed max-w-md">
            A premium digital concierge for professional networking. Whether you're seeking your next breakthrough or building a world-class team, we facilitate high-trust connections that matter.
          </p>
          <div className="flex flex-wrap items-center gap-3 mt-8">
            <Link
              to="/register"
              className="flex items-center gap-2 px-6 py-3 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-colors"
            >
              Get Started <ArrowRight size={16} />
            </Link>
            <button className="flex items-center gap-3 px-6 py-3 border border-gray-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-gray-50 transition-colors">
              <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>
          </div>
        </div>

        {/* Hero card */}
        <div className="relative">
          <div className="bg-slate-900 rounded-2xl overflow-hidden aspect-[4/3] flex items-end p-6">
            <div className="absolute top-4 right-4 bg-white/10 backdrop-blur-sm rounded-xl px-4 py-3 text-white">
              <p className="text-3xl font-bold">94%</p>
              <p className="text-xs text-white/70 mt-0.5">Hire Rate</p>
            </div>
            <div className="text-white/80 text-sm">
              Professional networking, elevated.
            </div>
          </div>
        </div>
      </section>

      {/* Get Vouched For */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
          {/* Left: stats card */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-gray-200 p-5 inline-flex items-center gap-3 shadow-sm">
              <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
                <Shield size={16} className="text-green-600" />
              </div>
              <span className="text-sm font-medium text-slate-700">Verified Trust</span>
            </div>
            <div className="bg-slate-900 rounded-2xl p-6 text-white max-w-xs">
              <p className="text-4xl font-bold">2.5x</p>
              <p className="text-slate-400 text-sm mt-1">Higher Accept Rate</p>
            </div>
          </div>

          {/* Right: copy */}
          <div>
            <h2 className="text-4xl font-bold text-slate-900 leading-tight">Get Vouched For.</h2>
            <p className="text-gray-500 mt-4 leading-relaxed">
              Stop shooting into the void of job boards. Access the hidden market by leveraging the reputation of people you know. Request referrals with professional elegance and track your status in real-time.
            </p>
            <div className="mt-6 space-y-3">
              {[
                'Intelligent Connection Mapping',
                'One-Click Referral Templates',
              ].map(f => (
                <div key={f} className="flex items-center gap-3">
                  <CheckCircle size={18} className="text-green-500 flex-shrink-0" />
                  <span className="text-slate-700 text-sm font-medium">{f}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Refer Talent */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-4xl font-bold text-slate-900 leading-tight">Refer Talent.</h2>
            <p className="text-gray-500 mt-4 leading-relaxed">
              Be the curator of your company's culture. Help your most talented connections bypass the noise and get straight to the hiring manager. Build your professional capital while helping your organization thrive.
            </p>
            <div className="mt-8 grid grid-cols-2 gap-4">
              {[
                { icon: Users, title: 'Build Your Team', desc: 'Influence the hiring process by bringing in proven talent from your network.' },
                { icon: Zap, title: 'Internal Credit', desc: 'Gain recognition for your role in sourcing top-tier candidates.' },
              ].map(({ icon: Icon, title, desc }) => (
                <div key={title} className="bg-gray-50 rounded-xl p-4">
                  <Icon size={20} className="text-slate-600 mb-2" />
                  <p className="font-semibold text-slate-900 text-sm">{title}</p>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Referral request card */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm max-w-sm ml-auto w-full">
            <div className="flex items-start gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                JS
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-900 text-sm">Referral Request</p>
                <p className="text-xs text-gray-400">2 min ago</p>
              </div>
              <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">New</span>
            </div>
            <p className="text-xs text-gray-500 italic leading-relaxed mb-4">
              "I've noticed you're hiring a Senior Product Designer. I've worked with David for 3 years at FinTech and he's exceptional..."
            </p>
            <div className="flex gap-2">
              <button className="flex-1 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition-colors">
                Approve & Refer
              </button>
              <button className="flex-1 py-2 border border-gray-200 text-xs font-semibold rounded-lg hover:bg-gray-50 transition-colors">
                View Profile
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <div className="inline-block text-xs font-semibold text-slate-500 bg-gray-200 px-3 py-1 rounded-full uppercase tracking-widest mb-6">
            Seamless Entry
          </div>
          <h2 className="text-4xl font-bold text-slate-900">Ready to expand your influence?</h2>
          <p className="text-gray-500 mt-4 text-lg">
            Join the thousands of professionals using Referly to build authentic careers. Access the platform instantly with your professional identity.
          </p>
          <div className="flex flex-wrap justify-center gap-3 mt-8">
            <Link
              to="/register"
              className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white text-sm font-semibold rounded-xl hover:bg-slate-800 transition-colors"
            >
              Sign up with Email
            </Link>
            <button className="flex items-center gap-2 px-5 py-2.5 border border-gray-200 bg-white rounded-xl text-sm font-medium text-slate-700 hover:bg-gray-50 transition-colors">
              <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Sign up with Google
            </button>
            <button className="flex items-center gap-2 px-5 py-2.5 bg-[#0077b5] text-white rounded-xl text-sm font-semibold hover:bg-[#006097] transition-colors">
              <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              Sign up with LinkedIn
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-4">Secure. Professional. One-Click Access.</p>
        </div>
      </section>

      <PublicFooter />
    </div>
  )
}
