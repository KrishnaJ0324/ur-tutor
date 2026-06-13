import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, GraduationCap } from 'lucide-react';
import { streamMessage } from '../api/tutorApi';
import type { HistoryMessage } from '../api/sessionApi';
import { ChoiceCard, type ChoiceData } from './ChoiceCard';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface Props {
  sessionId: string;
  initialMessages: HistoryMessage[];
  // Called after each assistant turn completes so the parent can refresh progress + sessions.
  onTurnComplete: () => void;
}

const CHOICES_OPEN = '[[CHOICES]]';
const CHOICES_RE = /\[\[CHOICES\]\]([\s\S]*?)\[\[\/CHOICES\]\]/;

// Text shown to the user = everything before the choices block.
const displayText = (raw: string) => {
  const i = raw.indexOf(CHOICES_OPEN);
  return (i === -1 ? raw : raw.slice(0, i)).trim();
};

const parseChoices = (raw: string): ChoiceData | null => {
  const m = raw.match(CHOICES_RE);
  if (!m) return null;
  try {
    const data = JSON.parse(m[1].trim());
    if (data && (data.kind === 'single' || data.kind === 'quiz')) return data as ChoiceData;
  } catch { /* incomplete/invalid block — ignore */ }
  return null;
};

const WelcomeCard = ({ onHintClick }: { onHintClick: (h: string) => void }) => (
  <div className="welcome-card">
    <div className="welcome-icon"><GraduationCap size={48} /></div>
    <h2 style={{ marginBottom: '8px' }}>UR Tutor</h2>
    <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '320px' }}>
      Tell me what you want to learn, or ask for a quiz. I'll teach one concept at a time and
      only mark a topic complete once you pass its quiz.
    </p>
    <div className="welcome-hints">
      {['Teach me Python loops', 'Quiz me on variables'].map(hint => (
        <span key={hint} className="hint-pill" style={{ cursor: 'pointer' }} onClick={() => onHintClick(hint)}>
          {hint}
        </span>
      ))}
    </div>
  </div>
);

export const Chat: React.FC<Props> = ({ sessionId, initialMessages, onTurnComplete }) => {
  const [messages, setMessages] = useState<Message[]>(
    initialMessages.map((m, i) => ({ id: `h${i}`, role: m.role, content: m.content }))
  );
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [choices, setChoices] = useState<ChoiceData | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  // Monotonic, collision-proof message ids. (Date.now()-based ids could collide between
  // the user bubble and the assistant bubble, making one mirror the other while streaming.)
  const idSeq = useRef(0);
  const newId = () => `m${idSeq.current++}`;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, choices]);

  const sendDirect = async (userMsg: string) => {
    if (!userMsg || isLoading) return;
    setChoices(null);

    setMessages(prev => [...prev, { id: newId(), role: 'user', content: userMsg }]);
    setIsLoading(true);

    const assistantId = newId();
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

    let raw = '';
    try {
      await streamMessage(userMsg, (chunk) => {
        raw += chunk;
        const shown = displayText(raw);
        setMessages(prev => prev.map(m => (m.id === assistantId ? { ...m, content: shown } : m)));
      }, sessionId);
      const parsed = parseChoices(raw);
      if (parsed) setChoices(parsed);
    } catch (err) {
      const msg = `⚠️ ${err instanceof Error ? err.message : 'Could not reach the backend.'}`;
      setMessages(prev => prev.map(m => (m.id === assistantId ? { ...m, content: m.content || msg } : m)));
    } finally {
      setIsLoading(false);
      onTurnComplete();
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const userMsg = input.trim();
    if (!userMsg) return;
    setInput('');
    sendDirect(userMsg);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-area">
        {messages.length === 0 ? (
          <WelcomeCard onHintClick={(hint) => sendDirect(hint)} />
        ) : (
          <div className="message-list">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-row ${msg.role}`}>
                <div className={`avatar ${msg.role}`}>{msg.role === 'user' ? 'U' : 'AI'}</div>
                <div className="bubble">
                  {msg.role === 'assistant' ? (
                    <div className="prose">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                      {isLoading && msg.content === '' && <span className="blinking-cursor">▋</span>}
                    </div>
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="input-area">
        {choices && (
          <div className="input-container">
            <ChoiceCard
              choices={choices}
              disabled={isLoading}
              onAnswer={(text) => { setChoices(null); sendDirect(text); }}
              onDismiss={() => setChoices(null)}
            />
          </div>
        )}
        <div className="input-container">
          <form onSubmit={handleSubmit} className="chat-form">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message UR Tutor…"
              className="chat-input"
              disabled={isLoading}
              autoComplete="off"
            />
            <button type="submit" disabled={!input.trim() || isLoading} className="send-btn">
              <Send size={14} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
