# ext-ai-enabled-ur-tutor-service

FastAPI-based educational AI tutoring service with multi-agent LangGraph orchestration, Socratic method teaching, quiz generation, and answer evaluation capabilities.

**Version:** `0.1.0`  
**Maintainer:** UR Tutor Development Team &lt;dev@urtutor.example.com&gt;

## Overview

UR Tutor is an AI-enabled educational backend service that provides intelligent tutoring through a multi-agent system. It orchestrates specialized LLM agents via LangGraph using a Supervisor Agent routing pattern to classify and handle user queries in three modes: teaching with Socratic methods, quiz generation, and answer evaluation. The system maintains session state and integrates with Google Generative AI (Gemini) to deliver personalized, structured learning experiences with comprehensive observability and error handling.

### Key Features

- Multi-agent tutoring system with Supervisor Agent routing pattern
- Socratic method implementation for interactive teaching
- Automated quiz generation and answer evaluation
- Session-based chat history with ephemeral in-memory state
- Structured output validation using Pydantic models
- Configurable temperature settings for LLM creativity control
- Comprehensive logging and error handling
- Streaming API responses for real-time interaction

### Dependencies

- FastAPI
- LangGraph
- Google Generative AI (Gemini)
- Pydantic
- Python 3.10+
- React
- TypeScript
- Vite

## API Documentation

- **Base URL:** `http://localhost:8000`
- **Authentication:** `none`
- **Swagger:** http://localhost:8000/docs

### Key Endpoints

- `POST /chat` — Send a message to the tutoring agent and receive a response with routing to teaching, quiz, or evaluation mode
- `POST /session` — Create a new tutoring session with unique session ID and initial state
- `GET /history/{session_id}` — Retrieve chat history for a specific tutoring session
- `POST /quiz/generate` — Generate a quiz based on the current topic or provided content
- `POST /evaluate` — Evaluate a student's answer and provide feedback

## Development

### Setup

1. Clone the repository: git clone https://github.com/KrishnaJ0324/ur-tutor.git
2. Install backend dependencies: pip install -r requirements.txt
3. Install frontend dependencies: cd frontend && npm install
4. Set up environment variables: cp .env.example .env and configure GOOGLE_API_KEY
5. Start the backend: python -m uvicorn backend.main:app --reload
6. Start the frontend: cd frontend && npm run dev

- **Start:** `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
- **Test:** `pytest backend/tests/ -v`
- **Build:** `cd frontend && npm run build && cd .. && python -m pip install -r requirements.txt`

## Deployment

- **Docker image:** `urtutor/ur-tutor-service:0.1.0`

### Environment Variables

- `GOOGLE_API_KEY` *(required)* — API key for Google Generative AI (Gemini) integration
- `LLM_TEMPERATURE` — Temperature setting for LLM responses (0.0-1.0); lower values for consistency, higher for creativity
- `SESSION_TIMEOUT` — Session timeout duration in seconds for ephemeral state cleanup
- `LOG_LEVEL` — Logging level for observability (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS` — Comma-separated list of allowed CORS origins for frontend communication
- `FRONTEND_URL` — URL where the frontend is deployed (e.g., http://localhost:5173)

## Latest Commit

**`01bf446`** by Krishna J — chore: removed loggers from chat.tsx file

- `frontend/src/App.tsx` — Removed all console logging statements (info, debug, error) from App.tsx across initialization, lifecycle, and event handling.
