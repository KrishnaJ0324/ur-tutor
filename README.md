# ur-tutor

## Overview

UR Tutor is an adaptive AI tutoring system that uses multiple specialized agents orchestrated by a supervisor to provide personalized teaching, quizzing, and evaluation. The system combines a FastAPI backend powered by LangGraph with a modern React frontend to deliver real-time conversational learning experiences with streaming responses.

## Key Modules

**Backend**: The backend is an adaptive AI tutoring system built on LangGraph and FastAPI that orchestrates multi-agent workflows through a router-based dispatcher. It implements a Supervisor Agent that intelligently routes user messages to specialized teaching, quiz, and evaluation agents, manages learner state through an in-memory GraphState structure, and exposes functionality via FastAPI HTTP endpoints that stream responses with embedded state metadata. All interactions are powered by Google Gemini models configured through a centralized LLM configuration layer, with workflow orchestration managed as a directed graph with memory checkpointing.

**Frontend**: The frontend is a modern React + TypeScript single-page application built with Vite that serves as the user-facing interface for the tutoring platform. It features a Chat component for real-time conversational interactions with streaming responses, a ProfileWidget for displaying learning statistics, and a tutorApi integration layer that manages session lifecycle and API communication. The application maintains a dark-mode glassmorphic design system with comprehensive CSS variables and is optimized for both development and production through Vite's build pipeline.

**Root**: The root module contains essential project configuration and documentation that establishes the foundation for the hybrid Node.js/Python technology stack. It includes `.gitignore` configuration for excluding build artifacts and environment files, and comprehensive README documentation that explains the system's multi-agent architecture and setup instructions.

## How It Works

When a user sends a message through the React frontend, the Chat component streams the request to the FastAPI backend via the tutorApi layer. The backend's Supervisor Agent analyzes the message and routes it to the appropriate specialized agent—teaching, quiz, or evaluation—based on the user's needs. The selected agent processes the request using the current learner state (topics, difficulty level, conversation history) and generates a contextual response. The backend streams this response word-by-word back to the frontend with embedded state metadata, which the Chat component displays in real-time. The system persists conversation state across requests using a temporary file-based chat store, enabling continuous learning sessions without a permanent database.

## Getting Started

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
export GOOGLE_API_KEY="your-api-key-here"
python -m uvicorn main:app --reload
```

The backend will start on `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`.

### Environment Configuration

Create a `.env` file in the backend directory with your Google Gemini API key:

```
GOOGLE_API_KEY=your-api-key-here
```

Visit `http://localhost:5173` in your browser to access the tutoring interface.

## Latest Commit

**`2f81aed`** by Krishna J — docs: refresh README via docbot

- `README.md` — The README was reformatted with simplified language, consolidated module descriptions, restructured Getting Started sections, and made code examples more concise and uniform.
