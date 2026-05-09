# ext-ai-enabled-ur-tutor-service

FastAPI-based adaptive AI tutoring system with multi-agent LangGraph architecture for intelligent content delivery, assessment, and grading.

**Version:** `0.1.0`  
**Maintainer:** UR Tutor Development Team &lt;krishnaj0324@example.com&gt;

## Overview

UR Tutor is an adaptive AI tutoring system that intelligently routes user requests to specialized agents for teaching, quizzing, and grading. It combines a FastAPI backend with a React frontend to deliver real-time, personalized learning experiences using multi-agent LangGraph architecture with ReAct reasoning patterns.

### Key Features

- Multi-agent routing system with teach, quiz, and eval specialized agents
- Real-time streaming responses with word-by-word delivery
- Adaptive difficulty and rubric adjustment based on user performance
- Session-based conversation history management
- Strict Pydantic validation to prevent AI hallucination
- Interactive React frontend with particle animations
- Tool-calling enabled autonomous ReAct reasoning

### Dependencies

- FastAPI
- LangGraph
- LangChain
- Pydantic
- React 19
- TypeScript
- Vite

## API Documentation

- **Base URL:** `http://localhost:8000`
- **Authentication:** `none`
- **Swagger:** http://localhost:8000/docs

### Key Endpoints

- `POST /chat` — Primary endpoint for streaming tutoring interactions; accepts user messages and returns word-by-word streaming responses with profile metadata
- `GET /health` — Health check endpoint to verify backend service availability

## Development

### Setup

1. Clone the repository: git clone https://github.com/KrishnaJ0324/ur-tutor.git
2. Install Python dependencies: pip install -r requirements.txt
3. Install Node dependencies: npm install in the frontend directory
4. Create .env file with LLM API keys (OPENAI_API_KEY or equivalent)
5. Initialize session storage directory for chat history

- **Start:** `fastapi dev backend/main.py`
- **Test:** `pytest backend/tests/`
- **Build:** `npm run build`

## Deployment

- **Docker image:** `ur-tutor:0.1.0`

### Environment Variables

- `OPENAI_API_KEY` *(required)* — API key for OpenAI LLM integration
- `LANGCHAIN_API_KEY` — API key for LangChain tracing and monitoring
- `SESSION_STORE_PATH` — File system path for persistent session and chat history storage
- `FRONTEND_URL` — CORS-allowed frontend URL for API requests
- `LOG_LEVEL` — Logging verbosity level (DEBUG, INFO, WARNING, ERROR)

## Latest Commit

**`01bf446`** by Krishna J — chore: removed loggers from chat.tsx file

- `frontend/src/App.tsx` — Removed all console logging statements from App.tsx across user ID generation, particles engine initialization, beforeunload handler registration, and reset button handling.
