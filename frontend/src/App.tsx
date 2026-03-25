import { useState, useEffect } from 'react';
import { Chat } from './components/Chat';
import { GraduationCap, RotateCcw } from 'lucide-react';
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";

function App() {
  const [userId] = useState(() => 'user-' + Math.random().toString(36).substring(2, 9));
  const [particlesReady, setParticlesReady] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => {
      setParticlesReady(true);
    });
  }, []);

  const handleReset = () => {
    if (window.confirm("Clear chat and start a new session?")) {
      window.location.reload();
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