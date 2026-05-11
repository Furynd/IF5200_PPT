import { Link } from 'react-router-dom'

export default function PublicFooter() {
  return (
    <footer className="bg-white border-t border-gray-200 py-8">
      <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-start justify-between gap-8">
        <div>
          <span className="font-bold text-slate-900 text-lg">Referly</span>
          <p className="text-xs text-gray-400 mt-1">© 2026 Referly. All rights reserved.</p>
          <p className="text-xs text-gray-400">Curating the future of professional connections through trust and transparency.</p>
        </div>
        <div className="flex gap-12 text-sm">
          <div>
            <p className="font-semibold text-slate-700 mb-2">Legal</p>
            <div className="space-y-1.5">
              <Link to="/privacy" className="block text-gray-500 hover:text-slate-900 transition-colors">Privacy Policy</Link>
              <Link to="/terms" className="block text-gray-500 hover:text-slate-900 transition-colors">Terms of Service</Link>
            </div>
          </div>
          <div>
            <p className="font-semibold text-slate-700 mb-2">Company</p>
            <div className="space-y-1.5">
              <Link to="/about" className="block text-gray-500 hover:text-slate-900 transition-colors">About</Link>
              <a href="#" className="block text-gray-500 hover:text-slate-900 transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
