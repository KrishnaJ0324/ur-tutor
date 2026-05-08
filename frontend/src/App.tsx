import { useState, useEffect } from 'react';
import { Chat } from './components/Chat';
import { GraduationCap, RotateCcw } from 'lucide-react';
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { endSession } from './api/tutorApi';

function App() {
  const [userId] = useState(() => {
    const id = 'user-' + Math.random().toString(36).substring(2, 9);
    console.info('[App] Generated new userId:', id);
    return id;
  });
  const [particlesReady, setParticlesReady] = useState(false);

  useEffect(() => {
    console.info('[App] Initializing particles engine');
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    })
      .then(() => {
        console.info('[App] Particles engine ready');
        setParticlesReady(true);
      })
      .catch((err) => {
        console.error('[App] Failed to initialize particles engine:', err);
      });
  }, []);

  useEffect(() => {
    console.debug('[App] Registering beforeunload handler for userId:', userId);
    const handleUnload = () => {
      console.info('[App] beforeunload fired — ending session for userId:', userId);
      endSession(userId);
    };
    window.addEventListener('beforeunload', handleUnload);
    return () => {
      console.debug('[App] Removing beforeunload handler for userId:', userId);
      window.removeEventListener('beforeunload', handleUnload);
    };
  }, [userId]);

  const handleReset = () => {
    console.info('[App] Reset button clicked');
    if (window.confirm("Clear chat and start a new session?")) {
      console.info('[App] Reset confirmed — reloading page');
      window.location.reload();
    } else {
      console.debug('[App] Reset cancelled by user');
    }
  };

  return (
    <div className="app-container" style={{ position: 'relative' }}>
      {particlesReady && (
        <Particles
          id="tsparticles"
          options={{
            background: { color: { value: "#0f1c70" } }, // Deep beautiful starry blue
            fpsLimit: 120,
            interactivity: {
              detectsOn: "window",
              events: {
                onClick: { enable: true, mode: "push" },
                onHover: { enable: true, mode: "repulse" },
              },
              modes: { push: { quantity: 3 }, repulse: { distance: 100, duration: 0.4 } },
            },
            particles: {
              color: { value: "#ffffff" }, // White stars
              links: { color: "#ffffff", distance: 150, enable: true, opacity: 0.3, width: 1 },
              move: { direction: "none", enable: true, outModes: { default: "bounce" }, random: false, speed: 0.3, straight: false },
              number: { density: { enable: true, width: 800 }, value: 60 },
              opacity: { value: 0.5 },
              shape: { type: "circle" },
              size: { value: { min: 1, max: 3 } },
            },
            detectRetina: true,
          }}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            zIndex: 0,
          }}
        />
      )}

      <header className="top-nav" style={{ position: 'relative', zIndex: 10, background: 'rgba(15, 15, 19, 0.8)', backdropFilter: 'blur(8px)' }}>
        <div className="nav-brand">
          <div className="brand-icon">
            <GraduationCap size={22} />
          </div>
          <span style={{ fontSize: '28px' }}>UR Tutor</span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="icon-btn" onClick={handleReset} title="Start Fresh">
            <RotateCcw size={22} />
          </button>
        </div>
      </header>

      <div className="main-content" style={{ position: 'relative', zIndex: 10 }}>
        <div className="chat-container">
          <Chat onStateUpdate={() => {}} userId={userId} />
        </div>
      </div>
    </div>
  );
}

export default App;