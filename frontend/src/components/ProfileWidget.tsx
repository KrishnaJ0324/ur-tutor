import React from 'react';

interface ProfileState {
  level: string;
  difficulty: string;
  accuracy_trend: number;
}

interface Props {
  state: ProfileState | null;
}

const Stat = ({ label, value, colorVar }: { label: string; value: string; colorVar?: string }) => (
  <div className="stat-item">
    <span className="stat-label">{label}</span>
    <span className="stat-value" style={{ color: colorVar ? `var(${colorVar})` : 'var(--text-primary)' }}>
      {value}
    </span>
  </div>
);

export const ProfileWidget: React.FC<Props> = ({ state }) => {
  if (!state) return null;

  const pct = Math.round(state.accuracy_trend * 100);
  const diffColor = state.difficulty === 'easy' ? '--easy' : state.difficulty === 'medium' ? '--medium' : '--hard';
  const barColor = pct >= 80 ? 'var(--easy)' : pct >= 50 ? 'var(--medium)' : 'var(--hard)';

  return (
    <div className="widget-card">
      <p className="widget-title">Current State</p>
      
      <div className="stat-grid">
        <Stat label="Level" value={state.level} />
        <Stat label="Difficulty" value={state.difficulty} colorVar={diffColor} />
      </div>

      <div>
        <div className="accuracy-header">
          <span className="stat-label">Accuracy</span>
          <span style={{ fontSize: '12px', fontWeight: 'bold', color: barColor }}>{pct}%</span>
        </div>
        <div className="accuracy-track">
          <div className="accuracy-fill" style={{ width: `${pct}%`, backgroundColor: barColor }} />
        </div>
      </div>
    </div>
  );
};