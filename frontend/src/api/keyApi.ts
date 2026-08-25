// src/api/keyApi.ts
// Bring-your-own-key: the user's Anthropic API key lives in this browser only. It is sent
// with each chat request (X-Anthropic-Key) and is never stored on the backend.
//
// Storage: sessionStorage by default, so the key is dropped when the tab closes and the
// window in which a script on this origin could read it stays as short as possible.
// localStorage is opt-in ("remember on this device") and survives restarts.
import { API_BASE_URL, getToken, forceLogout } from './authApi';

const KEY_STORAGE = 'ur_tutor_anthropic_key';

export const getApiKey = () =>
  sessionStorage.getItem(KEY_STORAGE) ?? localStorage.getItem(KEY_STORAGE) ?? '';
export const hasApiKey = () => getApiKey().length > 0;

/** True when the stored key persists across browser restarts. */
export const isRemembered = () => localStorage.getItem(KEY_STORAGE) !== null;

export const setApiKey = (k: string, remember: boolean) => {
  // Write one place and clear the other, so the two never disagree.
  const [target, other] = remember
    ? [localStorage, sessionStorage]
    : [sessionStorage, localStorage];
  target.setItem(KEY_STORAGE, k);
  other.removeItem(KEY_STORAGE);
};

export const clearApiKey = () => {
  sessionStorage.removeItem(KEY_STORAGE);
  localStorage.removeItem(KEY_STORAGE);
};

// Show enough of the key to recognise it, never the middle.
export const maskApiKey = (k: string) =>
  k.length <= 12 ? '••••' : `${k.slice(0, 7)}…${k.slice(-4)}`;

/** Ask the backend to verify a key with Anthropic before we save it. Costs no tokens. */
export async function validateApiKey(apiKey: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/key/validate`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  });
  if (res.status === 401) {
    forceLogout();
    throw new Error('Session expired');
  }
  if (!res.ok) {
    let detail = `Could not verify the key (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data.detail === 'string') detail = data.detail;
    } catch { /* non-JSON error body */ }
    throw new Error(detail);
  }
}
