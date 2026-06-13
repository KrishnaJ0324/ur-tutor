// src/api/sessionApi.ts
// Chat-session management (the left-panel conversation list).
import { API_BASE_URL, getToken, forceLogout } from './authApi';

export interface SessionInfo {
  id: string;
  title: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface HistoryMessage {
  role: 'user' | 'assistant';
  content: string;
}

function authHeaders(extra: Record<string, string> = {}) {
  return { Authorization: `Bearer ${getToken()}`, ...extra };
}

async function guard(res: Response): Promise<Response> {
  if (res.status === 401) {
    forceLogout();
    throw new Error('Session expired');
  }
  if (!res.ok) throw new Error(`Request failed (${res.status})`);
  return res;
}

export async function listSessions(): Promise<SessionInfo[]> {
  const res = await guard(await fetch(`${API_BASE_URL}/sessions`, { headers: authHeaders() }));
  return (await res.json()).sessions ?? [];
}

export async function createSession(): Promise<SessionInfo> {
  const res = await guard(await fetch(`${API_BASE_URL}/sessions`, { method: 'POST', headers: authHeaders() }));
  return res.json();
}

export async function deleteSession(id: string): Promise<void> {
  await guard(await fetch(`${API_BASE_URL}/sessions/${id}`, { method: 'DELETE', headers: authHeaders() }));
}

export async function getSessionMessages(id: string): Promise<HistoryMessage[]> {
  const res = await guard(await fetch(`${API_BASE_URL}/sessions/${id}/messages`, { headers: authHeaders() }));
  return (await res.json()).messages ?? [];
}
