# UR Tutor

## Overview

UR Tutor is an adaptive AI tutoring system that delivers personalized education through a multi-agent workflow orchestrated by LangGraph and LangChain. It combines a FastAPI backend with intelligent agent coordination and a modern React frontend to provide real-time, context-aware tutoring experiences with interactive quizzes and session persistence.

## Key Modules

**Backend**: An adaptive tutoring engine built on LangGraph that orchestrates four specialized agents—router, teach, quiz, and eval—to handle different aspects of the learning experience. The system maintains conversational context through a file-based session store, delivers streaming responses with embedded state metadata, and uses Pydantic models for type-safe validation. Recent refactoring has embraced declarative agent composition using LangChain's `create_agent` function, simplifying orchestration logic while delegating fine-grained response control to LLM reasoning.

**Frontend**: A React + TypeScript + Vite single-page application providing an interactive tutoring interface with real-time chat streaming, animated particle backgrounds, and interactive quizzes with difficulty selection. The component architecture separates concerns into a main App container, Chat component for message flows, and utility components like ProfileWidget for learning statistics, all styled with a cohesive dark-mode glassmorphic design system using CSS variables.

**Root**: The top-level project container that coordinates backend and frontend components, establishing project-wide conventions through standard .gitignore policies for Node.js, Python, and system files. It serves as the documentation hub and entry point, guiding developers through installation, configuration, and the system's supervisor-router agent architecture.

## How It Works

When a user sends a message, the FastAPI backend receives the request and routes it through a LangGraph state machine where a router agent performs semantic understanding to delegate the user intent to the appropriate agent (teach, quiz, or eval). The selected agent processes the request within the conversational context stored in a lightweight file-based session, generating a response that is streamed back to the React frontend word-by-word with embedded state metadata. The frontend displays the response in real-time while maintaining chat history across page reloads within the same session, and the system tracks learner progress and adapts future responses based on accumulated interaction context.

## Getting Started

1. **Clone the repository** and navigate to the project root directory.

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables** for the backend (API keys for Google Gemini, FastAPI settings, etc.) in a `.env` file.

5. **Start the backend server**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

6. **Start the frontend development server** (in a separate terminal):
   ```bash
   cd frontend
   npm run dev
   ```

7. **Open your browser** to the local development URL (typically `http://localhost:5173`) to access the UR Tutor application.