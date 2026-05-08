# ext-ai-enabled-tutor-service

LangGraph-based agentic tutoring system delivering adaptive education through multi-agent AI workflows with streaming REST API and React frontend.

**Version:** `0.1.0`  
**Maintainer:** UR Tutor Development Team &lt;team@urtutor.dev&gt;

## Overview

An AI-powered tutoring platform that orchestrates multi-agent workflows to provide adaptive, personalized education through Socratic teaching methods, interactive quizzes, and intelligent answer evaluation. The system combines LangGraph for agentic orchestration with LangChain for tool-calling and structured reasoning, enabling real-time educational interactions with streaming responses.

### Key Features

- LangGraph-based multi-agent orchestration with LLM-powered Supervisor routing
- Socratic teaching methodology through specialized Master Agent
- Dynamic quiz generation and answer evaluation with adaptive difficulty
- Session-aware conversational state management
- Streaming REST API responses for real-time interaction
- React frontend with TypeScript, Vite, and modern UI patterns
- Structured Pydantic validation and comprehensive logging

### Dependencies

- FastAPI
- LangGraph
- LangChain
- Google Generative AI
- Pydantic
- React
- TypeScript
- Vite

## API Documentation

- **Base URL:** `http://localhost:8000`
- **Authentication:** `none`
- **Swagger:** http://localhost:8000/docs

### Key Endpoints

- `POST /chat` — Main endpoint for tutoring interactions, accepts user messages and returns streaming educational responses
- `GET /session` — Retrieves current session state including student progress metrics and learning history
- `POST /quiz` — Initiates quiz workflow with difficulty selection and generates adaptive questions
- `POST /evaluate` — Evaluates student answers and provides detailed feedback with grading

## Development

### Setup

1. Clone the repository: git clone https://github.com/KrishnaJ0324/ur-tutor.git
2. Backend setup: cd backend && pip install -r requirements.txt
3. Frontend setup: cd ../frontend && npm install
4. Configure environment variables: cp .env.example .env and update Google Generative AI credentials
5. Initialize LLM configuration in backend/llm.py with your API keys

- **Start:** `cd backend && uvicorn main:app --reload & cd ../frontend && npm run dev`
- **Test:** `cd backend && pytest && cd ../frontend && npm run test`
- **Build:** `cd backend && pip install -r requirements.txt && cd ../frontend && npm run build`

## Deployment

- **Docker image:** `urtutor/ext-ai-enabled-tutor-service:0.1.0`

### Environment Variables

- `GOOGLE_API_KEY` *(required)* — API key for Google Generative AI services
- `FASTAPI_ENV` — Environment mode (development, production)
- `SESSION_TIMEOUT` — Session expiration time in minutes for file-based chat store
- `LOG_LEVEL` — Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS` — Comma-separated list of allowed CORS origins

## Latest Commit

**`99039a6`** by Krishna J — Merge branch 'main' of https://github.com/KrishnaJ0324/ur-tutor

- `README.md` — README.md was substantially restructured with a formal title change, expanded Overview with Key Features/Dependencies/API sections, reorganized Getting Started subsections, and updated the Latest Commit reference from evaluation.py to quiz.py.
