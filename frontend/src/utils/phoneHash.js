/**
 * Phone number normalization and SHA-256 hashing for contact discovery.
 *
 * This runs entirely client-side. The server never sees raw phone numbers
 * of non-users — only their hashes — matching the Signal/WhatsApp pattern
 * described by Marlinspike (2014).
 */

/**
 * Normalize Indonesian phone numbers to E.164 format (+62...).
 * Examples:
 *   "0812-3456-7890" → "+6281234567890"
 *   "62 812 3456 7890" → "+6281234567890"
 *   "+62 812 3456 7890" → "+6281234567890"
 *   "8123456789" → "+628123456789"
 */
export function normalizeIndonesianPhone(raw) {
  if (!raw || typeof raw !== 'string') return null

  // Strip everything except digits and leading +
  let cleaned = raw.trim().replace(/[^\d+]/g, '')

  // Handle + prefix
  if (cleaned.startsWith('+')) cleaned = cleaned.slice(1)

  // Already starts with country code 62
  if (cleaned.startsWith('62')) {
    // Validate rest is mobile: after 62, next digit should be 8
    if (cleaned[2] !== '8') return null
    return '+' + cleaned
  }

  // Starts with 0 (local format) → replace with 62
  if (cleaned.startsWith('0')) {
    if (cleaned[1] !== '8') return null
    return '+62' + cleaned.slice(1)
  }

  // Starts with 8 (user typed without prefix)
  if (cleaned.startsWith('8')) {
    return '+62' + cleaned
  }

  // Doesn't look like an Indonesian mobile number
  return null
}

/**
 * Validate that a normalized E.164 number is a plausible Indonesian mobile.
 * Indonesian mobile: +62 8xx xxxx xxxx (typically 10-12 digits after +62)
 */
export function isValidIndonesianMobile(e164) {
  return /^\+62[0-9]{9,13}$/.test(e164)
}

/**
 * SHA-256 hash of a string, returning hex digest.
 * Uses the Web Crypto API (available in all modern browsers + HTTPS contexts).
 */
export async function sha256Hex(text) {
  const encoder = new TextEncoder()
  const data = encoder.encode(text)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Process a list of raw phone numbers: normalize, validate, dedupe, hash.
 *
 * @param {string[]} rawNumbers - Raw input from user's contact list
 * @returns {Promise<{hashes: string[], invalid: number, total: number}>}
 */
export async function hashPhoneNumbers(rawNumbers) {
  if (!Array.isArray(rawNumbers)) return { hashes: [], invalid: 0, total: 0 }

  // Normalize all, filter invalid, dedupe
  const valid = new Set()
  let invalid = 0

  for (const raw of rawNumbers) {
    const normalized = normalizeIndonesianPhone(raw)
    if (normalized && isValidIndonesianMobile(normalized)) {
      valid.add(normalized)
    } else {
      invalid++
    }
  }

  // Hash the valid unique numbers
  const uniqueNumbers = Array.from(valid)
  const hashes = await Promise.all(uniqueNumbers.map(sha256Hex))

  return {
    hashes,
    invalid,
    total: rawNumbers.length,
  }
}
