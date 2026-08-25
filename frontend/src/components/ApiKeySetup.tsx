import React, { useState } from 'react';
import { KeyRound, X } from 'lucide-react';
import {
  getApiKey, setApiKey, clearApiKey, maskApiKey, validateApiKey, isRemembered,
} from '../api/keyApi';

interface Props {
  // True when the panel opened because a send was blocked — changes the copy only; the
  // panel always stays dismissible so the user is never trapped.
  required: boolean;
  onSaved: () => void;
  onClose: () => void;
}

/** The "add your Anthropic API key" panel. Shown from the nav, or when a send is blocked. */
export const ApiKeySetup: React.FC<Props> = ({ required, onSaved, onClose }) => {
  const existing = getApiKey();
  const [value, setValue] = useState('');
  const [remember, setRemember] = useState<boolean>(() => isRemembered());
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const key = value.trim();
    if (!key) return;
    setError('');
    setBusy(true);
    try {
      await validateApiKey(key);
      setApiKey(key, remember);
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not verify the key');
    } finally {
      setBusy(false);
    }
  };

  const remove = () => {
    clearApiKey();
    setValue('');
    onSaved();
  };

  return (
    <div className="key-overlay" onClick={onClose}>
      <form className="widget-card key-panel" onSubmit={submit} onClick={(e) => e.stopPropagation()}>
        <button type="button" className="icon-btn key-close" onClick={onClose} title="Close">
          <X size={18} />
        </button>

        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <div className="brand-icon" style={{ display: 'inline-flex' }}><KeyRound size={26} /></div>
          <h2 style={{ marginTop: 8 }}>Anthropic API key</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            {required
              ? 'UR Tutor runs on your own Anthropic key. Add one to start learning.'
              : 'Update or remove the key this browser uses.'}
          </p>
        </div>

        {existing && (
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 10 }}>
            Current key: <code>{maskApiKey(existing)}</code>{' '}
            <span style={{ opacity: 0.7 }}>
              ({isRemembered() ? 'saved on this device' : 'this tab only'})
            </span>
          </p>
        )}

        <input
          className="chat-input" style={{ width: '100%', marginBottom: 10 }}
          type="password" placeholder="sk-ant-…" value={value} autoComplete="off"
          onChange={(e) => setValue(e.target.value)} required
        />

        <label className="key-remember">
          <input
            type="checkbox" checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
          />
          <span>
            Remember on this device
            <em>Otherwise the key is forgotten when you close this tab.</em>
          </span>
        </label>

        {error && <p style={{ color: 'var(--hard)', fontSize: 13, margin: '4px 0' }}>{error}</p>}

        <button type="submit" className="quiz-submit-btn" style={{ width: '100%' }} disabled={busy}>
          {busy ? 'Verifying…' : existing ? 'Replace key' : 'Save key'}
        </button>

        {existing && (
          <button
            type="button" className="key-remove" onClick={remove}
            style={{ width: '100%', marginTop: 8 }}
          >
            Remove key from this browser
          </button>
        )}

        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 12, lineHeight: 1.5 }}>
          The key is kept in this browser and sent with each message so the tutor can call
          Claude on your behalf. It is never saved on the server. Create one at{' '}
          <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noreferrer"
             style={{ color: 'var(--accent)' }}>
            console.anthropic.com
          </a>.
        </p>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 8, lineHeight: 1.5 }}>
          Because it lives in your browser, use a <strong>dedicated key with a spend limit</strong>
          {' '}rather than your main one, and revoke it in the console when you are done.
        </p>
      </form>
    </div>
  );
};
