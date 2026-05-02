# ur-tutor

## Overview

UR Tutor is an adaptive AI tutoring system that combines a LangGraph-powered multi-agent backend with a modern React frontend to deliver personalized teaching, quizzing, and evaluation. The platform uses a Supervisor Agent router to dispatch student interactions to specialized teaching, quiz, and evaluation nodes, each equipped with LLM-driven agents and tool access. It provides a conversational chat interface where students receive real-time feedback and progress tracking.

## Key Modules

**Backend** — An adaptive tutoring orchestrator built on LangGraph and FastAPI that manages multi-agent AI workflows. It routes user messages through a Supervisor Agent to specialized teaching, quiz, and evaluation nodes, each powered by LangChain agents with tool access. The module uses file-based session storage and in-memory checkpoints for conversation history, with HTTP endpoints that bridge the React frontend to the educational agents while maintaining semantic routing and delegated tool invocation over explicit control flow.

**Frontend** — A modern React + TypeScript + Vite single-page application providing a conversational chat interface with particle animations, quiz functionality, and user profile tracking. It communicates with the backend through a centralized API layer (`tutorApi.ts`) that handles message streaming, session management, and chat history persistence. The UI implements a dark-mode glassmorphic design language using CSS variables and flexbox layouts, with session lifecycle management including graceful termination on browser close.

**Root** — The foundational documentation and configuration layer for the entire UR Tutor project. It contains project-level README documentation detailing the multi-agent architecture, standard development configuration files (`.gitignore`), and setup instructions that synchronize understanding between backend and frontend components.

## How It Works

When a student sends a message through the React frontend, it is transmitted to the FastAPI backend via the centralized API layer. The backend's Supervisor Agent receives the message and semantically routes it to the appropriate specialized node—teaching, quiz, or evaluation—based on the conversation context. The selected agent processes the request using LangChain tools and the configured LLM, generating an educational response enriched with formatting. The response is persisted to file-based session storage and returned to the frontend, where it appears in the chat interface. Conversation history is maintained in-memory within each session using LangGraph checkpoints, allowing continuity across multiple user interactions without requiring persistent database storage.

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/KrishnaJ0324/ur-tutor.git
   cd ur-tutor
   ```

2. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. In a new terminal, start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser to `http://localhost:5173` (or the URL provided by Vite) to access the UR Tutor interface.

### Configuration

Set up environment variables for LLM settings and API endpoints in a `.env` file in the backend directory before running the application.