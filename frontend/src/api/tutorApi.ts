// src/api/tutorApi.ts
// Tutor client: all calls carry the JWT. Streaming is plain text tokens from the deep agent
// (the old ||STATE|| side-channel is gone — progress now comes from GET /progress).
import { API_BASE_URL, getToken, forceLogout } from './authApi';

export interface ConceptProgress {
  name: string;
  mastered: boolean;
}

export interface TopicProgress {
  topic: string;
  difficulty?: string;
  status: string; // in_progress | complete | not_started
  percent: number;
  pass_threshold?: number;
  concepts: ConceptProgress[];
}

function authHeaders(extra: Record<string, string> = {}) {
  return { Authorization: `Bearer ${getToken()}`, ...extra };
}

export const streamMessage = async (
  message: string,
  onChunk: (text: string) => void,
  sessionId = 'main',
) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (response.status === 401) {
    forceLogout();
    throw new Error('Session expired');
  }
  if (!response.ok || !response.body) throw new Error(`Chat failed (${response.status})`);

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let done = false;
  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;
    if (value) onChunk(decoder.decode(value, { stream: true }));
  }
};

export const getProgress = async (): Promise<TopicProgress[]> => {
  const res = await fetch(`${API_BASE_URL}/progress`, { headers: authHeaders() });
  if (res.status === 401) {
    forceLogout();
    throw new Error('Session expired');
  }
  if (!res.ok) throw new Error(`Progress failed (${res.status})`);
  const data = await res.json();
  return data.topics ?? [];
};

export const resetSession = async (sessionId = 'main') => {
  await fetch(`${API_BASE_URL}/session/reset`, {
    method: 'POST',
    headers: authHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ session_id: sessionId }),
  });
};
