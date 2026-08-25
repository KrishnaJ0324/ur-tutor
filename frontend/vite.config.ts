import { defineConfig, loadEnv, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Emits Netlify's `dist/_headers` with a Content-Security-Policy.
 *
 * The user's Anthropic API key lives in this browser, so the security that matters is
 * keeping injected script from running and from phoning home. `connect-src` is generated
 * from the same VITE_API_BASE_URL the app calls, so the policy can never drift from the
 * backend it was built against (a mismatched origin would block every request).
 */
function securityHeaders(apiBaseUrl: string): Plugin {
  const apiOrigin = new URL(apiBaseUrl).origin
  const csp = [
    "default-src 'self'",
    "script-src 'self'",
    // React sets inline style attributes throughout, which style-src governs.
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self'",
    `connect-src 'self' ${apiOrigin}`,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ].join('; ')

  const headers = [
    '/*',
    `  Content-Security-Policy: ${csp}`,
    '  X-Content-Type-Options: nosniff',
    '  X-Frame-Options: DENY',
    '  Referrer-Policy: no-referrer',
    '  Permissions-Policy: geolocation=(), microphone=(), camera=()',
    '',
  ].join('\n')

  return {
    name: 'ur-tutor-security-headers',
    apply: 'build',
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: '_headers', source: headers })
    },
  }
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  return {
    plugins: [
      react(),
      securityHeaders(env.VITE_API_BASE_URL || 'http://localhost:8000'),
    ],
  }
})
