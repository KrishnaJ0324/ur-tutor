# ur-tutor

## Overview

UR Tutor is an intelligent multi-agent tutoring system that leverages LLMs and LangGraph to provide personalized educational interactions. It combines a Python FastAPI backend with a modern React frontend to deliver real-time, adaptive learning experiences through teaching, quizzing, and evaluation modes.

## Key Modules

**Backend**: A LangGraph-based multi-agent orchestration layer that routes user intents (teach, quiz, evaluate) through specialized agent nodes via a Supervisor Agent. It maintains ephemeral in-memory state with file-based session storage for chat history, and exposes pedagogical workflows through FastAPI endpoints that stream responses word-by-word with embedded metadata for real-time UI updates.

**Frontend**: A React + TypeScript + Vite single-page application providing an interactive tutoring interface with real-time chat, quiz functionality, and session persistence. It features animated particle effects, glassmorphic dark-mode design, markdown support, and API communication layers that stream tutor responses and track learning progress.

**Root**: The foundational project configuration layer that establishes development standards, governs version control practices, and documents system architecture. It orchestrates the integration of the distributed FastAPI backend and Vite-built frontend into a cohesive real-time multi-agent system.

## How It Works

When a user submits a query through the React frontend, the request is sent to the FastAPI backend, where a Supervisor Agent classifies the intent as teach, quiz, or evaluate. Based on this classification, the router dispatches the request to the appropriate specialized agent node (teach, quiz, or eval), which processes the pedagogical task using LangChain. The system maintains conversation state through in-memory GraphState and temporary file-based session storage, enabling continuity within a browser session. Responses are streamed word-by-word back to the frontend with embedded state metadata, allowing real-time UI updates and dynamic difficulty adjustment. The frontend displays responses with markdown formatting, animates particle effects for visual polish, and persists session data through beacon-based requests.

## Getting Started

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install Python dependencies: `pip install -r requirements.txt`
3. Configure environment variables (LLM API keys, etc.) in `.env`
4. Run the FastAPI server: `uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install Node.js dependencies: `npm install`
3. Start the Vite development server: `npm run dev`
4. Open your browser to `http://localhost:5173`

### Environment Configuration
Ensure backend API is accessible at `http://localhost:8000` from the frontend, and configure all required LLM provider API keys in the backend `.env` file before starting the development server.

## Latest Commit

**`163eb7a`** by Krishna J — added logger to evaluation.py

- `backend/agents/evaluation.py` — Added logging import, created module-level logger, and added try-except error handling with info/debug log statements around agent invocation.
