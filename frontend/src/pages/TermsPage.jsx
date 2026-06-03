import { CheckCircle, XCircle } from 'lucide-react'
import PublicNavbar from '../components/PublicNavbar'
import PublicFooter from '../components/PublicFooter'

const sections = [
  { id: 'account', label: 'Account Responsibilities' },
  { id: 'conduct', label: 'Prohibited Conduct' },
  { id: 'referral', label: 'Referral Guidelines' },
  { id: 'liability', label: 'Limitation of Liability' },
]

export default function TermsPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <PublicNavbar />

      <div className="max-w-6xl mx-auto px-6 py-16 flex-1">
        {/* Header */}
        <div className="mb-12">
          <div className="inline-block text-xs font-semibold text-slate-600 bg-gray-100 px-3 py-1 rounded-full uppercase tracking-widest mb-5">
            Legal Documentation
          </div>
          <h1 className="text-5xl font-bold text-slate-900">Terms of Service</h1>
          <p className="text-gray-500 mt-4">
            Last updated: October 24, 2026. These terms govern your use of the Referly platform and our curated networking services.
          </p>
        </div>

        <div className="grid md:grid-cols-[200px_1fr] gap-12">
          {/* TOC sidebar */}
          <aside>
            <div className="sticky top-20 bg-gray-50 rounded-xl border border-gray-200 p-4">
              <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">On This Page</p>
              <nav className="space-y-1">
                {sections.map(({ id, label }) => (
                  <a
                    key={id}
                    href={`#${id}`}
                    className="block text-sm text-gray-600 hover:text-slate-900 py-1 hover:pl-1 transition-all"
                  >
                    › {label}
                  </a>
                ))}
              </nav>
            </div>
          </aside>

          {/* Content */}
          <div className="space-y-12">
            {/* Account Responsibilities */}
            <section id="account">
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                <span className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">01</span>
                Account Responsibilities
              </h2>
              <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 mb-4">
                <p className="text-gray-600 leading-relaxed">
                  To access the curated features of Referly, you must register for an account. You represent and warrant that all information provided during registration is accurate and up-to-date.
                </p>
              </div>
              <div className="space-y-3">
                {[
                  'You are responsible for maintaining the confidentiality of your login credentials.',
                  'You must notify Referly immediately of any unauthorized use of your account.',
                  'Each account is individual; sharing professional credentials across multiple users is strictly prohibited.',
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle size={16} className="text-blue-500 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-gray-600 leading-relaxed">{item}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Prohibited Conduct */}
            <section id="conduct">
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                <span className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">02</span>
                Prohibited Conduct
              </h2>
              <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 mb-4">
                <p className="text-gray-600 leading-relaxed">
                  Our platform is designed for high-integrity networking. The following behaviors will result in immediate suspension or termination:
                </p>
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  { title: 'Misrepresentation', desc: 'Falsifying experience, credentials, or employment history.' },
                  { title: 'Harassment', desc: 'Unsolicited spam or aggressive communication with curators.' },
                  { title: 'Data Scraping', desc: 'Using automated tools to extract member data or job listings.' },
                  { title: 'Solicitation', desc: 'Selling access to referrals outside of platform-sanctioned mechanisms.' },
                ].map(({ title, desc }) => (
                  <div key={title} className="bg-white rounded-xl border border-red-100 p-4">
                    <div className="flex items-center gap-2 mb-1">
                      <XCircle size={15} className="text-red-400 flex-shrink-0" />
                      <p className="font-semibold text-slate-900 text-sm">{title}</p>
                    </div>
                    <p className="text-xs text-gray-500 leading-relaxed pl-5">{desc}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Referral Guidelines */}
            <section id="referral">
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                <span className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">03</span>
                Referral Guidelines
              </h2>
              <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 mb-4">
                <p className="text-gray-600 leading-relaxed mb-5">
                  Referly operates on a mutual-trust model. When providing a referral, you acknowledge:
                </p>
                <div className="space-y-4">
                  {[
                    {
                      title: 'Authenticity Requirement',
                      desc: 'Referrals must be based on genuine professional interaction. Automated or "blind" referrals are not permitted.',
                    },
                    {
                      title: 'Privacy and Discretion',
                      desc: 'The content of internal referral notes is strictly confidential and must not be shared outside the platform.',
                    },
                  ].map(({ title, desc }) => (
                    <div key={title} className="flex gap-3">
                      <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <CheckCircle size={12} className="text-blue-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900 text-sm">{title}</p>
                        <p className="text-sm text-gray-500 mt-0.5 leading-relaxed">{desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Limitation of Liability */}
            <section id="liability">
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 mb-4">
                <span className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">04</span>
                Limitation of Liability
              </h2>
              <div className="bg-slate-900 rounded-xl p-6 mb-4">
                <p className="text-slate-300 text-xs leading-relaxed uppercase tracking-wide font-mono">
                  "TO THE MAXIMUM EXTENT PERMITTED BY LAW, REFERLY SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES, RESULTING FROM (A) YOUR ACCESS TO OR USE OF OR INABILITY TO ACCESS OR USE THE SERVICES; (B) ANY CONDUCT OR CONTENT OF ANY THIRD PARTY ON THE SERVICES; OR (C) UNAUTHORIZED ACCESS, USE OR ALTERATION OF YOUR TRANSMISSIONS OR CONTENT."
                </p>
              </div>
              <p className="text-sm text-gray-500 leading-relaxed">
                The content of internal referral notes is strictly confidential and must not be shared outside the platform-sanctioned mechanisms.
              </p>
            </section>
          </div>
        </div>
      </div>

      <PublicFooter />
    </div>
  )
}
