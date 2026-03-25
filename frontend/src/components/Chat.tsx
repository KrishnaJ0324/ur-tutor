import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, GraduationCap, CheckCircle } from 'lucide-react';
import { streamMessage, type ProfileState, type QuizQuestion } from '../api/tutorApi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Props {
  onStateUpdate: (state: ProfileState) => void;
  userId: string;
}

const WelcomeCard = ({ onHintClick }: { onHintClick: (h: string) => void }) => (
  <div className="welcome-card">
    <div className="welcome-icon">
      <GraduationCap size={48} />
    </div>
    <h2 style={{ marginBottom: '8px' }}>UR Tutor</h2>
    <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '300px' }}>
      Tell me what you want to learn, or ask for a quiz. I'll adapt to your pace.
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

export const Chat: React.FC<Props> = ({ onStateUpdate, userId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeQuiz, setActiveQuiz] = useState<QuizQuestion[] | null>(null);
  const [needsDifficulty, setNeedsDifficulty] = useState<boolean>(false);
  const [quizAnswers, setQuizAnswers] = useState<{[key: number]: string}>({});
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendDirect = async (userMsg: string) => {
    if (!userMsg || isLoading) return;

    const newMsg: Message = { id: Date.now().toString(), role: 'user', content: userMsg, timestamp: new Date() };
    setMessages(prev => [...prev, newMsg]);
    setIsLoading(true);

    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '', timestamp: new Date() }]);

    try {
      await streamMessage(userId, userMsg, 
        (chunk) => {
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMsgId ? { ...msg, content: msg.content + chunk } : msg
          ));
        },
        (newState) => {
          onStateUpdate(newState);
          if (newState.active_quiz !== undefined) {
            setActiveQuiz(newState.active_quiz);
            if (!newState.active_quiz) {
               setQuizAnswers({});
            }
          }
          if (newState.needs_difficulty !== undefined) {
             setNeedsDifficulty(newState.needs_difficulty);
          }
        }
      );
    } catch {
      setMessages(prev => prev.map(msg => 
        msg.id === assistantMsgId 
          ? { ...msg, content: '⚠️ Could not reach the backend.' } 
          : msg
      ));
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userMsg = input.trim();
    if (!userMsg) return;
    setInput('');
    await sendDirect(userMsg);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const handleQuizSubmit = () => {
    if (!activeQuiz) return;
    
    // Check if fully answered
    if (Object.keys(quizAnswers).length < activeQuiz.length) {
      alert("Please answer all questions before submitting.");
      return;
    }
    
    // Format submission manually as an aggregated letter string
    let submissionString = "";
    activeQuiz.forEach((q) => {
      const selectedOption = quizAnswers[q.id];
      // Find letter index A, B, C, D
      const optionIndex = q.options.indexOf(selectedOption);
      const letter = ["A", "B", "C", "D"][optionIndex] || "?";
      submissionString += `${q.id}. ${letter} - ${selectedOption}\n`;
    });
    
    setActiveQuiz(null); // Optimistically hide modal
    sendDirect(submissionString);
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
                <div className={`avatar ${msg.role}`}>
                  {msg.role === 'user' ? 'U' : 'AI'}
                </div>
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
        {needsDifficulty && (
          <div className="quiz-panel" style={{ textAlign: 'center' }}>
            <h3 className="quiz-title" style={{ justifyContent: 'center' }}>Select Your Level</h3>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '8px' }}>
              {['Beginner', 'Intermediate', 'Advanced'].map(lvl => (
                <button
                  key={lvl}
                  onClick={() => {
                    setNeedsDifficulty(false);
                    sendDirect(lvl);
                  }}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: 'transparent',
                    border: '1px solid var(--accent)',
                    borderRadius: '8px',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '16px',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => {
                     e.currentTarget.style.backgroundColor = 'var(--accent)';
                  }}
                  onMouseOut={(e) => {
                     e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>
        )}

        {activeQuiz && activeQuiz.length > 0 && (
          <div className="quiz-panel">
            <h3 className="quiz-title">Interactive Quiz</h3>
            {activeQuiz.map((q) => (
              <div key={q.id} className="quiz-question-block">
                <p className="quiz-q-text"><strong>{q.id}.</strong> {q.question}</p>
                <div className="quiz-options">
                  {q.options.map((opt, idx) => {
                    const letter = ["A", "B", "C", "D"][idx];
                    return (
                      <label key={idx} className="quiz-option-label">
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          value={opt}
                          checked={quizAnswers[q.id] === opt}
                          onChange={() => setQuizAnswers(prev => ({...prev, [q.id]: opt}))}
                        />
                        <span className="quiz-option-text"><strong>{letter})</strong> {opt}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
            <button 
              onClick={handleQuizSubmit} 
              className="quiz-submit-btn"
              disabled={isLoading || Object.keys(quizAnswers).length < activeQuiz.length}
            >
              <CheckCircle size={16} style={{marginRight: '6px'}}/> Submit Quiz
            </button>
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
              placeholder={activeQuiz ? "Please answer the quiz above..." : (needsDifficulty ? "Please select a level..." : "Message UR Tutor...")}
              className="chat-input"
              disabled={isLoading || (activeQuiz !== null && activeQuiz.length > 0) || needsDifficulty}
              autoComplete="off"
            />
            <button type="submit" disabled={!input.trim() || isLoading || (activeQuiz !== null && activeQuiz.length > 0) || needsDifficulty} className="send-btn">
              <Send size={14} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};