# ext-ai-enabled-adaptive-tutoring-engine

An adaptive AI tutoring system built on LangGraph that orchestrates specialized teaching, quiz, and evaluation agents powered by Google Gemini LLM to deliver personalized learning experiences.

**Version:** `0.1.0`  
**Maintainer:** UR Tutor Development Team &lt;dev@urtutor.local&gt;

## Overview

UR Tutor is an interactive AI-powered tutoring platform that combines LangGraph-based multi-agent orchestration with Socratic teaching methods to deliver adaptive, personalized learning experiences. The system dynamically routes between specialized agents (teach, quiz, evaluate) based on user intent and learner profile state, maintaining comprehensive progress tracking and educational metrics.

### Key Features

- Multi-agent LangGraph orchestration with teach, quiz, and evaluate agents
- Real-time streaming responses powered by Google Gemini LLM
- Adaptive difficulty level management based on learner performance
- Session persistence with file-based chat history and progress tracking
- Comprehensive learner profile metrics and performance analytics
- Type-safe state machine for conversation flow management
- React 19 frontend with real-time quiz interactions and particle animations

### Dependencies

- FastAPI
- LangGraph
- Google Gemini API
- React 19
- TypeScript
- Vite
- Python 3.8+
- Node.js 18+

## API Documentation

- **Base URL:** `http://localhost:8000`
- **Authentication:** `none`
- **Swagger:** http://localhost:8000/docs

### Key Endpoints

- `POST /chat` — Send a message to the tutoring system and receive a streamed response from the appropriate agent (teach, quiz, or evaluate)
- `GET /profile` — Retrieve the current learner profile metrics including progress, difficulty level, and performance statistics
- `POST /session` — Initialize a new tutoring session with optional learner context
- `GET /history` — Fetch the chat history and interaction records for the current session

## Development

### Setup

1. Clone the repository: git clone https://github.com/KrishnaJ0324/ur-tutor.git
2. Install backend dependencies: cd backend && pip install -r requirements.txt
3. Install frontend dependencies: cd frontend && npm install
4. Configure Google Gemini API key in backend/.env
5. Set up file-based session storage directory in backend/

- **Start:** `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 & cd frontend && npm run dev`
- **Test:** `cd backend && pytest tests/ && cd frontend && npm run test`
- **Build:** `cd frontend && npm run build && cd backend && pip install -e .`

## Deployment

- **Docker image:** `krishnaj0324/ur-tutor:0.1.0`

### Environment Variables

- `GOOGLE_GEMINI_API_KEY` *(required)* — API key for Google Gemini LLM service
- `FASTAPI_HOST` — Host address for FastAPI backend server
- `FASTAPI_PORT` — Port number for FastAPI backend server (default: 8000)
- `SESSION_STORAGE_PATH` — File system path for storing session data and chat history
- `LOG_LEVEL` — Logging verbosity level (DEBUG, INFO, WARNING, ERROR)
- `REACT_API_URL` — Base URL for frontend to communicate with backend API

## Latest Commit

**`01bf446`** by Krishna J — chore: removed loggers from chat.tsx file

- `frontend/src/App.tsx` — Removed all console logging statements from App.tsx across user ID generation, particles engine initialization, beforeunload handler registration, and reset button handling.
