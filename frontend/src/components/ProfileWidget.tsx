import React from 'react';
import { CheckCircle } from 'lucide-react';
import type { TopicProgress } from '../api/tutorApi';

interface Props {
  topics: TopicProgress[];
}

const barColor = (pct: number, complete: boolean) =>
  complete ? 'var(--easy)' : pct >= 50 ? 'var(--medium)' : 'var(--hard)';

export const ProfileWidget: React.FC<Props> = ({ topics }) => {
  return (
    <div className="widget-card" style={{ minWidth: 240 }}>
      <p className="widget-title">Your Progress</p>
      {topics.length === 0 ? (
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
          No topics yet — ask the tutor to teach you something.
        </p>
      ) : (
        topics.map((t) => {
          const complete = t.status === 'complete';
          return (
            <div key={t.topic} style={{ marginBottom: 14 }}>
              <div className="accuracy-header" style={{ alignItems: 'center' }}>
                <span className="stat-label" style={{ fontWeight: 600 }}>{t.topic}</span>
                {complete ? (
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: 'var(--easy)', fontSize: 12, fontWeight: 700 }}>
                    <CheckCircle size={14} /> COMPLETE
                  </span>
                ) : (
                  <span style={{ fontSize: 12, fontWeight: 700, color: barColor(t.percent, false) }}>{t.percent}%</span>
                )}
              </div>
              <div className="accuracy-track">
                <div className="accuracy-fill" style={{ width: `${t.percent}%`, backgroundColor: barColor(t.percent, complete) }} />
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};
