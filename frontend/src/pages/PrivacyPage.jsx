import { User, FileText, Monitor, Share2, CheckCircle } from 'lucide-react'
import PublicNavbar from '../components/PublicNavbar'
import PublicFooter from '../components/PublicFooter'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <PublicNavbar />

      <div className="max-w-4xl mx-auto px-6 py-16 flex-1">
        {/* Header */}
        <div className="mb-10">
          <div className="inline-block text-xs font-semibold text-slate-600 bg-gray-100 px-3 py-1 rounded-full uppercase tracking-widest mb-5">
            Trust &amp; Transparency
          </div>
          <h1 className="text-5xl font-bold text-slate-900">Privacy Policy</h1>
          <p className="text-gray-500 mt-4 leading-relaxed">
            Last updated: October 24, 2026. At Referly, your trust is our most valuable currency. We are committed to protecting your professional data with the highest standards of security.
          </p>
        </div>

        {/* Introduction */}
        <div className="bg-gray-50 rounded-2xl border border-gray-200 p-8 mb-10">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-4">
            <span className="w-6 h-px bg-slate-900 inline-block" /> Introduction
          </h2>
          <p className="text-gray-600 leading-relaxed mb-3">
            This Privacy Policy describes how Referly ("we", "us", or "our") collects, uses, and shares your personal information when you use our high-end networking and referral platform. By accessing Referly, you consent to the data practices described in this policy.
          </p>
          <p className="text-gray-600 leading-relaxed">
            We prioritize an editorial networking experience, which means we only ask for the information necessary to build meaningful professional connections and facilitate high-quality job referrals.
          </p>
        </div>

        {/* Data Collection */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">Data Collection</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {[
              {
                icon: User,
                title: 'Identity Information',
                desc: 'We collect full name, professional title, and contact details (email and phone) to create your unique curator profile.',
              },
              {
                icon: FileText,
                title: 'Professional Background',
                desc: 'Experience history, education details, and uploaded CVs are processed to power our intelligent referral matching engine.',
              },
              {
                icon: Monitor,
                title: 'Technical Data',
                desc: 'We log IP addresses, browser types, and interaction patterns to ensure platform stability and protect against fraudulent activity.',
              },
              {
                icon: Share2,
                title: 'Social Graph',
                desc: 'Information about your professional connections and shared history helps us curate a more relevant network experience for you.',
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center mb-3">
                  <Icon size={18} className="text-slate-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-1">{title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Use of Information */}
        <div className="bg-gray-50 rounded-2xl border border-gray-200 p-8 mb-10">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-5">
            <FileText size={18} className="text-slate-600" /> Use of Information
          </h2>
          <div className="space-y-4">
            {[
              {
                title: 'Service Personalization',
                desc: 'We use your data to tailor job opportunities and connection suggestions that align with your specific career trajectory.',
              },
              {
                title: 'Communication Management',
                desc: 'To send critical updates regarding referral requests, platform changes, or security alerts.',
              },
              {
                title: 'Platform Integrity',
                desc: 'Monitoring for spam, verifying identities, and ensuring that all referrals maintain a high standard of professional ethics.',
              },
            ].map(({ title, desc }) => (
              <div key={title} className="flex gap-3">
                <CheckCircle size={18} className="text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-900">{title}</p>
                  <p className="text-sm text-gray-500 mt-0.5 leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* User Rights */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">User Rights</h2>
          <p className="text-gray-500 mb-6 leading-relaxed">
            Under global data protection regulations (including GDPR), you maintain full control over your professional digital footprint. You have the following irrevocable rights:
          </p>
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              {
                title: 'Access',
                desc: 'The right to request a complete export of all data we hold about your professional profile.',
              },
              {
                title: 'Erasure',
                desc: 'Commonly known as the "right to be forgotten", you can request the permanent deletion of your account at any time.',
              },
              {
                title: 'Correction',
                desc: 'The right to rectify any inaccurate or incomplete professional information within our records.',
              },
            ].map(({ title, desc }) => (
              <div key={title} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">{title}</p>
                <p className="text-sm text-gray-600 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <PublicFooter />
    </div>
  )
}
