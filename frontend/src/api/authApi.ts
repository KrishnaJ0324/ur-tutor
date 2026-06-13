// src/api/authApi.ts
// Auth client: register / login (OAuth2 password flow) / me, plus JWT storage.
// In production set VITE_API_BASE_URL (e.g. https://your-app.onrender.com) at build time.
export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) || 'http://localhost:8000';
const TOKEN_KEY = 'ur_tutor_token';

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

// Broadcast a forced logout (e.g. a 401) so the app can drop back to the login screen.
export const forceLogout = () => {
  clearToken();
  window.dispatchEvent(new Event('ur-unauthorized'));
};

async function detail(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
  } catch {
    return `Request failed (${res.status})`;
  }
}

export async function register(username: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(await detail(res));
  const data = await res.json();
  setToken(data.access_token);
}

export async function login(username: string, password: string): Promise<void> {
  // OAuth2 password flow expects form-encoded username/password.
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${API_BASE_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) throw new Error(await detail(res));
  const data = await res.json();
  setToken(data.access_token);
}

export interface Me {
  id: number;
  username: string;
}

export async function getMe(): Promise<Me> {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (res.status === 401) {
    forceLogout();
    throw new Error('Session expired');
  }
  if (!res.ok) throw new Error(await detail(res));
  return res.json();
}

export function logout() {
  clearToken();
}
