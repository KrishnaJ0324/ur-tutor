import { useState, useEffect, useCallback } from 'react';
import { Chat } from './components/Chat';
import { Login } from './components/Login';
import { ProfileWidget } from './components/ProfileWidget';
import { GraduationCap, LogOut, Plus, Trash2 } from 'lucide-react';
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { getToken, logout as clearAuth, getMe, type Me } from './api/authApi';
import { getProgress, type TopicProgress } from './api/tutorApi';
import {
  listSessions, createSession, deleteSession, getSessionMessages,
  type SessionInfo, type HistoryMessage,
} from './api/sessionApi';

function App() {
  const [authed, setAuthed] = useState<boolean>(() => !!getToken());
  const [me, setMe] = useState<Me | null>(null);
  const [topics, setTopics] = useState<TopicProgress[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryMessage[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [particlesReady, setParticlesReady] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine) => { await loadSlim(engine); }).then(() => setParticlesReady(true));
  }, []);

  useEffect(() => {
    const onUnauth = () => { setAuthed(false); setMe(null); };
    window.addEventListener('ur-unauthorized', onUnauth);
    return () => window.removeEventListener('ur-unauthorized', onUnauth);
  }, []);

  const refreshProgress = useCallback(() => {
    getProgress().then(setTopics).catch(() => {});
  }, []);

  const refreshSessions = useCallback(async (): Promise<SessionInfo[]> => {
    try {
      const list = await listSessions();
      setSessions(list);
      return list;
    } catch { return []; }
  }, []);

  // Bootstrap once authenticated: load identity, progress, sessions (create one if none).
  useEffect(() => {
    if (!authed) return;
    getMe().then(setMe).catch(() => {});
    refreshProgress();
    (async () => {
      let list = await refreshSessions();
      if (list.length === 0) {
        const cs = await createSession();
        list = [cs];
        setSessions(list);
      }
      setActiveId(list[0].id);
    })();
  }, [authed, refreshProgress, refreshSessions]);

  // Load transcript whenever the active session changes.
  useEffect(() => {
    if (!authed || !activeId) return;
    setHistoryLoading(true);
    getSessionMessages(activeId)
      .then(setHistory)
      .catch(() => setHistory([]))
      .finally(() => setHistoryLoading(false));
  }, [authed, activeId]);

  const handleNewSession = async () => {
    const cs = await createSession();
    setSessions(prev => [cs, ...prev]);
    setHistory([]);
    setActiveId(cs.id);
  };

  const handleDeleteSession = async (id: string) => {
    if (!window.confirm('Delete this conversation? (Topic progress is kept.)')) return;
    await deleteSession(id);
    const remaining = sessions.filter(s => s.id !== id);
    setSessions(remaining);
    if (activeId === id) {
      if (remaining.length > 0) setActiveId(remaining[0].id);
      else { const cs = await createSession(); setSessions([cs]); setActiveId(cs.id); }
    }
  };

  const handleTurnComplete = () => {
    refreshProgress();
    refreshSessions(); // titles + ordering may have changed
  };

  const handleLogout = () => {
    clearAuth();
    setAuthed(false);
    setMe(null);
    setTopics([]);
    setSessions([]);
    setActiveId(null);
  };

  if (!authed) return <Login onAuthed={() => setAuthed(true)} />;

  return (
    <div className="app-container" style={{ position: 'relative' }}>
      {particlesReady && (
        <Particles
          id="tsparticles"
          options={{
            background: { color: { value: "#0f1c70" } },
            fpsLimit: 120,
            interactivity: {
              detectsOn: "window",
              events: { onClick: { enable: true, mode: "push" }, onHover: { enable: true, mode: "repulse" } },
              modes: { push: { quantity: 3 }, repulse: { distance: 100, duration: 0.4 } },
            },
            particles: {
              color: { value: "#ffffff" },
              links: { color: "#ffffff", distance: 150, enable: true, opacity: 0.3, width: 1 },
              move: { direction: "none", enable: true, outModes: { default: "bounce" }, random: false, speed: 0.3, straight: false },
              number: { density: { enable: true, width: 800 }, value: 60 },
              opacity: { value: 0.5 }, shape: { type: "circle" }, size: { value: { min: 1, max: 3 } },
            },
            detectRetina: true,
          }}
          style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", zIndex: 0 }}
        />
      )}

      <header className="top-nav" style={{ position: 'relative', zIndex: 10, background: 'rgba(15, 15, 19, 0.8)', backdropFilter: 'blur(8px)' }}>
        <div className="nav-brand">
          <div className="brand-icon"><GraduationCap size={22} /></div>
          <span style={{ fontSize: '20px' }}>UR Tutor</span>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {me && <span style={{ color: 'white', fontSize: 14, opacity: 0.85 }}>@{me.username}</span>}
          <button className="icon-btn" onClick={handleLogout} title="Log out"><LogOut size={20} /></button>
        </div>
      </header>

      <div className="main-content" style={{ position: 'relative', zIndex: 10 }}>
        <aside className="sidebar">
          <button className="new-session-btn" onClick={handleNewSession}>
            <Plus size={16} /> New session
          </button>

          <div className="session-list">
            {sessions.map(s => (
              <div
                key={s.id}
                className={`session-item ${s.id === activeId ? 'active' : ''}`}
                onClick={() => setActiveId(s.id)}
              >
                <span className="session-title">{s.title || 'New chat'}</span>
                <button
                  className="session-del"
                  title="Delete"
                  onClick={(e) => { e.stopPropagation(); handleDeleteSession(s.id); }}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>

          <ProfileWidget topics={topics} />
        </aside>

        {activeId && !historyLoading ? (
          <Chat key={activeId} sessionId={activeId} initialMessages={history} onTurnComplete={handleTurnComplete} />
        ) : (
          <div className="chat-container" style={{ alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
            Loading…
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
