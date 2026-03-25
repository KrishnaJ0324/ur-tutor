// src/api/tutorApi.ts
// In production, the backend and frontend share the exact same domain, so the URL root is blank.
const API_BASE_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';

export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
}

export interface ProfileState {
  level: string;
  difficulty: string;
  accuracy_trend: number;
  active_quiz?: QuizQuestion[] | null;
  needs_difficulty?: boolean;
}

export const streamMessage = async (
  userId: string, 
  message: string, 
  onChunk: (text: string) => void,
  onStateUpdate: (state: ProfileState) => void
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, message: message }),
    });

    if (!response.body) throw new Error('No response body');

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let done = false;

    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      const chunkValue = decoder.decode(value, { stream: true });
      
      // Look for a state update hidden in the stream (optional backend implementation)
      // Example: Backend sends "||STATE:{"level":"beginner"}||"
      if (chunkValue.includes('||STATE:')) {
        try {
          const stateStr = chunkValue.split('||STATE:')[1].split('||')[0];
          onStateUpdate(JSON.parse(stateStr));
          // Remove the state data from the text shown to the user
          onChunk(chunkValue.replace(`||STATE:${stateStr}||`, ''));
        } catch (e) {
          console.error("Failed to parse state from stream", e);
        }
      } else {
        // Normal text chunk
        onChunk(chunkValue);
      }
    }
  } catch (error) {
    console.error('Streaming error:', error);
    throw error;
  }
};

export const resetProfile = async (userId: string) => {
  await fetch(`${API_BASE_URL}/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message: "" }),
  });
};