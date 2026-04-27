import { Link } from 'react-router-dom'
import { Shield, Heart, Lock, CheckCircle } from 'lucide-react'
import PublicNavbar from '../components/PublicNavbar'
import PublicFooter from '../components/PublicFooter'

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <PublicNavbar />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <div className="inline-block text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-1 rounded-full uppercase tracking-widest mb-5">
            Our Mission
          </div>
          <h1 className="text-5xl font-bold text-slate-900 leading-tight">
            Bridging the Talent Gap through High-Trust Referrals
          </h1>
          <p className="text-gray-500 mt-5 leading-relaxed">
            We believe the best opportunities shouldn't be hidden behind algorithms. We're rebuilding professional networking on a foundation of genuine human trust.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center gap-2 mt-8 px-6 py-3 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-colors"
          >
            Explore Opportunities
          </Link>
        </div>

        {/* Testimonial card */}
        <div className="relative">
          <div className="bg-slate-900 rounded-2xl overflow-hidden aspect-[4/3] p-8 flex items-end">
            <div className="bg-white rounded-xl p-4 shadow-lg max-w-xs">
              <p className="text-sm italic text-slate-700">
                "Referly changed how I think. The quality of trust is unmatched."
              </p>
              <p className="text-xs text-gray-400 mt-2">— Sarah Moreno</p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-16 items-center">
          <div className="bg-slate-900 rounded-2xl aspect-[4/3]" />
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Our Story</h2>
            <p className="text-gray-500 mt-4 leading-relaxed">
              The traditional job application process is broken. Thousands of qualified candidates get lost in automated filters, while great companies struggle to find genuine talent.
            </p>
            <p className="text-gray-500 mt-3 leading-relaxed">
              Referly was born out of a simple observation: the most successful hires consistently come from internal referrals. We decided to democratize that access.
            </p>
            <p className="font-semibold text-slate-900 mt-4 leading-relaxed">
              We help professionals skip the application queue by connecting them directly with employees who can vouch for their skills and fit.
            </p>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-slate-900 text-center">How it Works</h2>
          <p className="text-gray-500 text-center mt-2 max-w-xl mx-auto">
            A seamless ecosystem designed for both those seeking new heights and those helping others get there.
          </p>

          <div className="grid md:grid-cols-2 gap-6 mt-12">
            {/* For Applicants */}
            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-200">
              <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center mb-6">
                <span className="text-sm font-bold text-slate-700">A</span>
              </div>
              <h3 className="font-bold text-slate-900 mb-5">For Applicants</h3>
              <div className="space-y-4">
                {[
                  { n: '01', title: 'Discover Roles', desc: 'Access a curated list of high-impact positions across top-tier firms.' },
                  { n: '02', title: 'Connect with Insiders', desc: 'Find employees at your target companies who are ready to refer.' },
                  { n: '03', title: 'Skip the Queue', desc: "Get your profile directly to the hiring manager's desk with a trust-backed referral." },
                ].map(({ n, title, desc }) => (
                  <div key={n} className="flex gap-4">
                    <span className="text-xs font-bold text-gray-400 pt-0.5 flex-shrink-0">{n}</span>
                    <div>
                      <p className="font-semibold text-slate-900 text-sm">{title}</p>
                      <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* For Employees */}
            <div className="bg-slate-900 rounded-2xl p-8">
              <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center mb-6">
                <span className="text-sm font-bold text-white">E</span>
              </div>
              <h3 className="font-bold text-white mb-5">For Employees</h3>
              <div className="space-y-4">
                {[
                  { title: 'Monetize Your Network', desc: 'Turn your professional network into opportunities by helping those in your contacts find their next role.' },
                  { title: 'Build Team Quality', desc: 'Make your company stronger by sharing opportunities with the right talent.' },
                  { title: 'Automated Management', desc: 'Let Referly handle the logistics. CV management, status updates, and automated matching.' },
                ].map(({ title, desc }) => (
                  <div key={title} className="flex gap-3">
                    <CheckCircle size={16} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-white text-sm">{title}</p>
                      <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Values */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-slate-900 mb-2">Our Values</h2>
          <div className="w-12 h-1 bg-slate-900 mb-10" />
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              { icon: Shield, title: 'Professionalism', desc: 'We maintain an elite ecosystem where quality interactions are the standard. Every referral is a professional endorsement of excellence.' },
              { icon: Heart, title: 'Trust', desc: 'Trust is our primary currency. Our verification systems ensure that connections are meaningful and endorsements are sincere.' },
              { icon: Lock, title: 'Privacy', desc: 'Data security is foundational. We prioritize the privacy of our referrers and applicants with enterprise-grade encrypted and secure protocols.' },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="bg-white rounded-xl p-6 border border-gray-200">
                <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center mb-4">
                  <Icon size={20} className="text-slate-600" />
                </div>
                <h3 className="font-bold text-slate-900 mb-2">{title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-6 text-center bg-slate-900 rounded-2xl py-16">
          <h2 className="text-3xl font-bold text-white">Ready to bypass the traditional queue?</h2>
          <p className="text-slate-400 mt-3">Join the future of hiring and start making connections that matter today.</p>
          <Link
            to="/register"
            className="inline-block mt-8 px-8 py-3 bg-white text-slate-900 font-semibold rounded-xl hover:bg-gray-100 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </section>

      <PublicFooter />
    </div>
  )
}
