# ext-ai-enabled-tutor-service

LangGraph-based adaptive AI tutoring system with multi-agent orchestration, Socratic method instruction, and real-time streaming responses for personalized learning.

**Version:** `0.1.0`  
**Maintainer:** UR Tutor Development Team &lt;dev@urtutor.example.com&gt;

## Overview

UR Tutor is an AI-powered adaptive tutoring platform that delivers personalized instruction through a multi-agent orchestration system. It uses LangGraph for workflow coordination, implements the Socratic method for teaching, generates contextual quizzes, and provides real-time streaming responses to create an engaging learning experience tailored to individual student needs.

### Key Features

- Multi-agent orchestration with supervisor routing via LangGraph
- Socratic method-based teaching agent for adaptive instruction
- Dynamic quiz generation and grading evaluation
- Real-time streaming responses with word-by-word output
- Session state management with file-based storage
- Pydantic schema validation to prevent LLM hallucination
- Google Gemini dual-instance configuration for creativity and consistency

### Dependencies

- langchain
- langgraph
- google-generativeai
- fastapi
- pydantic
- react
- typescript
- vite

## API Documentation

- **Base URL:** `http://localhost:8000`
- **Authentication:** `none`
- **Swagger:** http://localhost:8000/docs

### Key Endpoints

- `POST /chat` — Submit user message and receive AI tutoring response with streaming
- `POST /quiz` — Request dynamically generated quiz questions based on learning topic
- `POST /grade` — Submit quiz answers for evaluation and receive grading feedback
- `GET /session` — Retrieve current session state and learning progress metrics

## Development

### Setup

1. Clone the repository: git clone https://github.com/KrishnaJ0324/ur-tutor.git
2. Install backend dependencies: cd backend && pip install -r requirements.txt
3. Install frontend dependencies: cd frontend && npm install
4. Configure environment variables: cp .env.example .env and update with your API keys
5. Initialize Google Gemini API credentials in backend configuration

- **Start:** `python backend/main.py`
- **Test:** `pytest backend/tests/`
- **Build:** `cd frontend && npm run build`

## Deployment

- **Docker image:** `urtutor/ur-tutor-service:0.1.0`

### Environment Variables

- `GOOGLE_API_KEY` *(required)* — Google Generative AI API key for Gemini model access
- `SESSION_STORAGE_PATH` — File system path for session state storage
- `GEMINI_TEMPERATURE_TEACH` — Temperature setting for teaching agent (creativity level)
- `GEMINI_TEMPERATURE_QUIZ` — Temperature setting for quiz agent (consistency level)
- `FRONTEND_URL` — URL of the React frontend application

## Latest Commit

**`08889e0`** by Krishna J — added logger to quiz.py

- `backend/agents/quiz.py` — Added logging import, logger initialization, and three logging statements (invocation start, exception handling, and completion tracking) to the quiz_node function.
