import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, X, ArrowRight, CheckCircle } from 'lucide-react';

export interface ChoiceData {
  kind: 'single' | 'quiz';
  question?: string;
  options?: string[];
  topic?: string;
  questions?: { q: string; options: string[] }[];
}

interface Props {
  choices: ChoiceData;
  disabled?: boolean;
  onAnswer: (text: string) => void;
  onDismiss: () => void;
}

const Row = ({ n, text, selected, onClick, showArrow }: {
  n: number; text: string; selected?: boolean; onClick: () => void; showArrow?: boolean;
}) => (
  <button type="button" className={`choice-row ${selected ? 'selected' : ''}`} onClick={onClick}>
    <span className="choice-num">{n}</span>
    <span className="choice-text">{text}</span>
    {showArrow && <ArrowRight size={16} className="choice-arrow" />}
  </button>
);

export const ChoiceCard: React.FC<Props> = ({ choices, disabled, onAnswer, onDismiss }) => {
  const isQuiz = choices.kind === 'quiz' && !!choices.questions?.length;
  const questions = choices.questions ?? [];
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});

  // --- Single choice (e.g. difficulty) — click sends immediately ---
  if (!isQuiz) {
    return (
      <div className="choice-card">
        <div className="choice-head">
          <span className="choice-q">{choices.question || 'Choose one'}</span>
          <button className="choice-x" onClick={onDismiss} title="Dismiss"><X size={16} /></button>
        </div>
        {(choices.options ?? []).map((opt, i) => (
          <Row key={i} n={i + 1} text={opt} showArrow onClick={() => !disabled && onAnswer(opt)} />
        ))}
      </div>
    );
  }

  // --- Quiz — paginated, select per question, then submit all ---
  const q = questions[idx];
  const allAnswered = questions.every((_, i) => answers[i] !== undefined);
  const isLast = idx === questions.length - 1;

  const submit = () => {
    const text =
      'Here are my quiz answers:\n' +
      questions.map((_, i) => `${i + 1}. ${answers[i]}`).join('\n');
    onAnswer(text);
  };

  return (
    <div className="choice-card">
      <div className="choice-head">
        <span className="choice-q">{q.q}</span>
        <div className="choice-nav">
          <button disabled={idx === 0} onClick={() => setIdx(i => Math.max(0, i - 1))}><ChevronLeft size={16} /></button>
          <span className="choice-page">{idx + 1} of {questions.length}</span>
          <button disabled={isLast} onClick={() => setIdx(i => Math.min(questions.length - 1, i + 1))}><ChevronRight size={16} /></button>
          <button className="choice-x" onClick={onDismiss} title="Dismiss"><X size={16} /></button>
        </div>
      </div>

      {q.options.map((opt, i) => (
        <Row
          key={i}
          n={i + 1}
          text={opt}
          selected={answers[idx] === opt}
          onClick={() => setAnswers(prev => ({ ...prev, [idx]: opt }))}
        />
      ))}

      <div className="choice-footer">
        {isLast ? (
          <button className="choice-submit" disabled={disabled || !allAnswered} onClick={submit}>
            <CheckCircle size={15} style={{ marginRight: 6 }} />
            {allAnswered ? 'Submit answers' : `Answer all ${questions.length} questions`}
          </button>
        ) : (
          <button
            className="choice-submit"
            disabled={answers[idx] === undefined}
            onClick={() => setIdx(i => Math.min(questions.length - 1, i + 1))}
          >
            Next <ArrowRight size={15} style={{ marginLeft: 6 }} />
          </button>
        )}
      </div>
    </div>
  );
};
