import React, { useState } from 'react';
import { GraduationCap } from 'lucide-react';
import { login, register } from '../api/authApi';

interface Props {
  onAuthed: () => void;
}

export const Login: React.FC<Props> = ({ onAuthed }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      if (mode === 'register') {
        await register(username.trim(), password);
      } else {
        await login(username.trim(), password);
      }
      onAuthed();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: '#0f1c70',
    }}>
      <form onSubmit={submit} className="widget-card" style={{ width: 340, padding: 28 }}>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <div className="brand-icon" style={{ display: 'inline-flex' }}>
            <GraduationCap size={28} />
          </div>
          <h2 style={{ marginTop: 8 }}>UR Tutor</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            {mode === 'login' ? 'Sign in to continue learning' : 'Create an account'}
          </p>
        </div>

        <input
          className="chat-input" style={{ width: '100%', marginBottom: 10 }}
          placeholder="Username" value={username} autoComplete="username"
          onChange={(e) => setUsername(e.target.value)} required minLength={3}
        />
        <input
          className="chat-input" style={{ width: '100%', marginBottom: 10 }}
          type="password" placeholder="Password" value={password}
          autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          onChange={(e) => setPassword(e.target.value)} required minLength={6}
        />

        {error && <p style={{ color: 'var(--hard)', fontSize: 13, margin: '4px 0' }}>{error}</p>}

        <button type="submit" className="quiz-submit-btn" style={{ width: '100%' }} disabled={busy}>
          {busy ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Register'}
        </button>

        <p style={{ textAlign: 'center', fontSize: 13, marginTop: 12, color: 'var(--text-secondary)' }}>
          {mode === 'login' ? "No account? " : 'Already registered? '}
          <span
            style={{ color: 'var(--accent)', cursor: 'pointer' }}
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
          >
            {mode === 'login' ? 'Register' : 'Sign in'}
          </span>
        </p>
      </form>
    </div>
  );
};
