# int-ai-enabled-ur-tutor-service

An adaptive AI tutoring system built on LangGraph that orchestrates specialized AI agents for personalized teaching, quizzing, and evaluation using Google's Gemini LLM.

**Version:** `0.1.0`  
**Maintainer:** UR Tutor Development Team &lt;krishnaj0324@example.com&gt;

## Overview

UR Tutor is an adaptive AI tutoring platform that leverages LangGraph multi-agent orchestration to deliver personalized educational experiences. The system intelligently routes user requests to specialized teach, quiz, and eval agents powered by Google's Gemini LLM, maintaining learner profiles and chat history to enable context-aware, difficulty-adaptive instruction.

### Key Features

- Multi-agent orchestration with intelligent request routing
- Personalized adaptive teaching with dynamic pedagogical content
- Difficulty-calibrated quiz generation with randomized multiple-choice questions
- Context-aware submission evaluation with rubric-based grading
- Real-time streaming chat interface with markdown content rendering
- Learner profile tracking with accuracy and difficulty metrics
- Session persistence with file-based chat history management
- Production-ready logging and monitoring throughout API endpoints

### Dependencies

- FastAPI
- LangGraph
- Google Gemini LLM
- Pydantic
- React 19
- TypeScript
- Vite
- axios

## API Documentation

- **Base URL:** `http://localhost:8000`
- **Authentication:** `none`
- **Swagger:** http://localhost:8000/docs

### Key Endpoints

- `POST /api/chat/stream` — Stream-based chat endpoint for user interactions with the tutoring system
- `POST /api/session` — Create a new tutoring session with learner profile initialization
- `GET /api/session/{session_id}` — Retrieve chat history and session state for a given session
- `GET /api/profile` — Fetch current learner profile including difficulty level and accuracy metrics

## Development

### Setup

1. Clone the repository: git clone https://github.com/KrishnaJ0324/ur-tutor.git
2. Install backend dependencies: cd backend && pip install -r requirements.txt
3. Install frontend dependencies: cd frontend && npm install
4. Configure environment variables in backend/.env with GOOGLE_API_KEY and other settings
5. Ensure Python 3.10+ and Node.js 18+ are installed

- **Start:** `cd backend && uvicorn main:app --reload`
- **Test:** `pytest backend/tests -v`
- **Build:** `cd frontend && npm run build`

## Deployment

- **Docker image:** `ur-tutor-service:0.1.0`

### Environment Variables

- `GOOGLE_API_KEY` *(required)* — API key for Google Gemini LLM access
- `FASTAPI_ENV` — Environment mode (development, production, testing)
- `LLM_TEMPERATURE_TEACH` — Temperature setting for teach agent (0.7 recommended)
- `LLM_TEMPERATURE_QUIZ` — Temperature setting for quiz agent (0.3 recommended)
- `SESSION_STORAGE_PATH` — File-based session storage directory path
- `LOG_LEVEL` — Logging level (INFO, DEBUG, ERROR)

## Latest Commit

**`aff2b2f`** by Krishna J — added loggers to routes.py

- `backend/api/routes.py` — Added comprehensive logging throughout routes.py by importing the logging module, creating a logger instance, and inserting log statements at key execution points across all endpoints.
