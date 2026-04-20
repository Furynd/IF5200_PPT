import { useState } from 'react'
import { X, Upload, Clipboard, AlertCircle, Loader2, Check } from 'lucide-react'
import { hashPhoneNumbers } from '../utils/phoneHash'
import { api } from '../lib/api'

/**
 * Contact Sync Modal — web MVP approach.
 *
 * On mobile, we'd use expo-contacts to read the address book directly.
 * On web, we need another input method. Three options shown here:
 *   1. Paste numbers from WhatsApp/Contacts export
 *   2. Upload a CSV (one number per line or first column)
 *   3. Manual entry (for testing)
 */

const INPUT_MODES = {
  PASTE: 'paste',
  CSV: 'csv',
  MANUAL: 'manual',
}

export default function ContactSyncModal({ open, onClose, onSuccess }) {
  const [mode, setMode] = useState(INPUT_MODES.PASTE)
  const [pastedText, setPastedText] = useState('')
  const [csvFile, setCsvFile] = useState(null)
  const [manualNumbers, setManualNumbers] = useState([''])
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  if (!open) return null

  const reset = () => {
    setPastedText('')
    setCsvFile(null)
    setManualNumbers([''])
    setResult(null)
    setError('')
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  // Parse raw numbers from the current input mode
  const collectRawNumbers = async () => {
    if (mode === INPUT_MODES.PASTE) {
      // Split by newlines, commas, or semicolons
      return pastedText.split(/[\n,;]+/).map(s => s.trim()).filter(Boolean)
    }
    if (mode === INPUT_MODES.MANUAL) {
      return manualNumbers.map(s => s.trim()).filter(Boolean)
    }
    if (mode === INPUT_MODES.CSV && csvFile) {
      const text = await csvFile.text()
      // For CSV: take first column, skip header if it looks like one
      const lines = text.split(/\r?\n/)
      const numbers = []
      for (const line of lines) {
        const firstCol = line.split(',')[0]?.trim().replace(/^["']|["']$/g, '')
        if (!firstCol) continue
        // Skip likely header row
        if (numbers.length === 0 && /phone|number|kontak|nomor|tel/i.test(firstCol)) continue
        numbers.push(firstCol)
      }
      return numbers
    }
    return []
  }

  const handleSync = async () => {
    setError('')
    setProcessing(true)
    setResult(null)

    try {
      const rawNumbers = await collectRawNumbers()
      if (rawNumbers.length === 0) {
        setError('Tidak ada nomor yang bisa diproses. Silakan periksa input Anda.')
        setProcessing(false)
        return
      }

      // Client-side: normalize + hash
      const { hashes, invalid, total } = await hashPhoneNumbers(rawNumbers)

      if (hashes.length === 0) {
        setError(
          `Tidak ada nomor valid ditemukan dari ${total} input. ` +
          `Pastikan nomor berformat Indonesia (08xxxxxxxx atau +628xxxxxxxx).`
        )
        setProcessing(false)
        return
      }

      // Send hashes to server for matching
      const response = await api.syncContacts(hashes)

      setResult({
        total,
        valid: hashes.length,
        invalid,
        matched: response.matched_count,
        ghostsCreated: response.ghosts_created,
        connectionsCreated: response.connections_created,
      })

      // Notify parent if connections were created
      if (response.connections_created > 0 && onSuccess) {
        onSuccess(response)
      }
    } catch (err) {
      setError(err.message || 'Gagal memproses kontak. Silakan coba lagi.')
    } finally {
      setProcessing(false)
    }
  }

  // Success screen
  if (result) {
    return (
      <ModalShell onClose={handleClose}>
        <div className="text-center py-4">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <Check size={24} className="text-green-600" />
          </div>
          <h3 className="text-lg font-bold">Sinkronisasi Berhasil</h3>
          <p className="text-gray-500 text-sm mt-1">Kontakmu telah dicocokkan.</p>

          <div className="mt-6 space-y-2 text-sm text-left bg-surface-50 rounded-lg p-4">
            <StatRow label="Total nomor diproses" value={result.total} />
            <StatRow label="Nomor valid" value={result.valid} />
            {result.invalid > 0 && (
              <StatRow label="Nomor tidak valid" value={result.invalid} muted />
            )}
            <hr className="border-surface-200 my-2" />
            <StatRow
              label="Koneksi baru ditemukan"
              value={result.connectionsCreated}
              highlight
            />
            <StatRow label="Belum terdaftar di Referly" value={result.ghostsCreated} muted />
          </div>

          {result.connectionsCreated === 0 && (
            <p className="text-xs text-gray-400 mt-4">
              Kontakmu yang belum terdaftar akan otomatis terhubung saat mereka bergabung.
            </p>
          )}

          <button
            onClick={handleClose}
            className="mt-6 w-full py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700"
          >
            Selesai
          </button>
        </div>
      </ModalShell>
    )
  }

  // Input screen
  return (
    <ModalShell onClose={handleClose}>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-bold">Sinkronkan Kontak</h3>
          <p className="text-sm text-gray-500 mt-1">
            Nomor akan di-hash di perangkatmu sebelum dikirim. Kami tidak pernah melihat nomor mentah dari kontakmu.
          </p>
        </div>

        {/* Mode tabs */}
        <div className="flex gap-1 p-1 bg-surface-100 rounded-lg">
          <ModeTab
            active={mode === INPUT_MODES.PASTE}
            onClick={() => setMode(INPUT_MODES.PASTE)}
            icon={Clipboard}
            label="Tempel"
          />
          <ModeTab
            active={mode === INPUT_MODES.CSV}
            onClick={() => setMode(INPUT_MODES.CSV)}
            icon={Upload}
            label="CSV"
          />
          <ModeTab
            active={mode === INPUT_MODES.MANUAL}
            onClick={() => setMode(INPUT_MODES.MANUAL)}
            icon={Clipboard}
            label="Manual"
          />
        </div>

        {/* Mode-specific input */}
        {mode === INPUT_MODES.PASTE && (
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              Tempel daftar nomor telepon
            </label>
            <textarea
              value={pastedText}
              onChange={e => setPastedText(e.target.value)}
              placeholder={"08123456789\n0815111222\n+628137890123"}
              rows={6}
              disabled={processing}
              className="w-full px-3 py-2 border border-surface-200 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
            />
            <p className="text-xs text-gray-400 mt-1">Satu nomor per baris, atau pisahkan dengan koma.</p>
          </div>
        )}

        {mode === INPUT_MODES.CSV && (
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Unggah file CSV</label>
            <input
              type="file"
              accept=".csv,.txt"
              onChange={e => setCsvFile(e.target.files?.[0] || null)}
              disabled={processing}
              className="w-full text-sm text-gray-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-primary-50 file:text-primary-700 file:font-medium hover:file:bg-primary-100"
            />
            <p className="text-xs text-gray-400 mt-1">
              Nomor telepon di kolom pertama. Header opsional.
            </p>
          </div>
        )}

        {mode === INPUT_MODES.MANUAL && (
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 block">Masukkan nomor satu per satu</label>
            {manualNumbers.map((num, idx) => (
              <input
                key={idx}
                type="tel"
                value={num}
                onChange={e => {
                  const next = [...manualNumbers]
                  next[idx] = e.target.value
                  if (idx === manualNumbers.length - 1 && e.target.value.trim()) {
                    next.push('')
                  }
                  setManualNumbers(next)
                }}
                placeholder="08123456789"
                disabled={processing}
                className="w-full px-3 py-2 border border-surface-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-surface-100"
              />
            ))}
          </div>
        )}

        {error && (
          <div className="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">
            <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={handleClose}
            disabled={processing}
            className="px-4 py-2.5 border border-surface-200 rounded-lg font-medium hover:bg-surface-50 disabled:opacity-50"
          >
            Batal
          </button>
          <button
            onClick={handleSync}
            disabled={processing}
            className="flex-1 py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {processing ? (
              <><Loader2 size={16} className="animate-spin" /> Memproses...</>
            ) : (
              'Sinkronkan'
            )}
          </button>
        </div>
      </div>
    </ModalShell>
  )
}

// ── Sub-components ──────────────────────────────────────

function ModalShell({ children, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-auto"
        onClick={e => e.stopPropagation()}
      >
        <div className="relative p-6">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-lg hover:bg-surface-100"
          >
            <X size={18} className="text-gray-400" />
          </button>
          {children}
        </div>
      </div>
    </div>
  )
}

function ModeTab({ active, onClick, icon: Icon, label }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-md text-sm font-medium transition-colors ${
        active ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'
      }`}
    >
      <Icon size={14} />
      {label}
    </button>
  )
}

function StatRow({ label, value, highlight, muted }) {
  return (
    <div className="flex items-center justify-between">
      <span className={muted ? 'text-gray-500' : 'text-gray-700'}>{label}</span>
      <span className={`font-semibold ${
        highlight ? 'text-primary-600 text-lg' : muted ? 'text-gray-500' : 'text-gray-900'
      }`}>
        {value}
      </span>
    </div>
  )
}
