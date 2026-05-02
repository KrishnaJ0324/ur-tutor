# ur-tutor

## Overview

UR Tutor is an adaptive AI tutoring system that uses multi-agent orchestration to deliver personalized learning experiences. It combines a LangGraph-based backend with specialized teaching, quiz, and evaluation agents alongside a modern React frontend to create an interactive tutoring interface.

## Key Modules

**Backend**: Implements an adaptive tutoring workflow using LangGraph and LangChain, with a Supervisor Agent that routes user intents to specialized agents (teach, quiz, eval). It integrates Google Generative AI for inference, FastAPI for HTTP routing, and maintains conversational state through in-memory session management with checkpointing. Each agent uses LangChain's `create_agent` function with explicit Tool objects to handle LLM invocations, and the API streams responses with embedded state metadata to enable reactive UI updates.

**Frontend**: A React 19 + TypeScript + Vite single-page application providing an interactive chat interface with real-time message streaming, adaptive difficulty selection, and quiz panels. It communicates with the backend through a RESTful API layer (`tutorApi.ts`), maintains client-side session state, and features a dark-mode glassmorphic design system for an engaging user experience.

## How It Works

When a user sends a message, the frontend streams it to the backend REST API. The backend's Supervisor Agent analyzes the intent and routes the request to the appropriate specialized agent node (teach, quiz, or eval). The selected agent generates a response using Google Generative AI and relevant tools, with all conversational state tracked through LangGraph's StateGraph. The backend returns the response with embedded state metadata, which the frontend uses to update the UI reactively and maintain session continuity. Chat history is persisted within the user session, allowing the system to maintain context across multiple conversational turns without requiring permanent database storage.

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/KrishnaJ0324/ur-tutor.git
cd ur-tutor

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### Configuration

Create a `.env` file in the backend directory with your Google Generative AI API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### Running the Application

```bash
# Start the backend (from backend directory)
uvicorn main:app --reload

# Start the frontend (from frontend directory)
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.