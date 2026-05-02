# UR Tutor

## Overview

UR Tutor is an AI-powered educational tutoring system that delivers personalized learning experiences through a multi-agent architecture. It uses Google's Gemini LLM to implement Socratic teaching methods, adapting lessons and assessments in real-time based on student interactions. The system combines a FastAPI backend orchestrating intelligent agents with a modern React frontend providing an intuitive chat-based learning interface.

## Key Modules

**Backend**: A FastAPI service that orchestrates multi-agent learning workflows using LangGraph. It implements specialized agents for routing user intents (teach, quiz, evaluate), generating adaptive lessons, creating difficulty-calibrated quiz questions, and grading responses. All agents leverage Google's Gemini LLM with temperature-tuned configurations, while state management uses in-memory LangGraph with optional session persistence through file-based chat storage.

**Frontend**: A React + TypeScript single-page application built with Vite that serves as the user interface for UR Tutor. It features a responsive chat-based tutoring interface with animated particle backgrounds, real-time message streaming, and interactive quiz functionality. The architecture includes conversation management, user progress tracking, and session persistence, styled with a dark-mode glassmorphic design system.

**Root**: The foundational configuration and documentation layer establishing development standards, code organization, and contributor onboarding. It includes `.gitignore` rules for Python and Node.js artifacts, and comprehensive README documentation covering architecture, module organization, and setup procedures for both backend and frontend components.

## How It Works

A user interacts with the React frontend by submitting a message or quiz response, which sends an HTTP request to the FastAPI backend at `localhost:8000`. The backend's router agent receives the request and dispatches it to the appropriate specialized agent—teaching, quiz, or evaluation—based on the user's intent. The selected agent processes the request using Google's Gemini LLM and returns a streamed response with embedded state metadata. The frontend receives the streamed response in real-time, updating the chat interface and displaying UI elements like quiz questions or progress indicators. Session state is maintained in-memory during the conversation, with optional persistence to file-based storage for chat history retrieval.

## Getting Started

### Backend Setup
1. Clone the repository: `git clone https://github.com/KrishnaJ0324/ur-tutor.git`
2. Navigate to the backend directory: `cd backend`
3. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set environment variables (Google Gemini API key, etc.) in a `.env` file
6. Start the server: `uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`
4. Open your browser to `http://localhost:5173`

### Environment Configuration
- Create a `.env` file in the root directory with required API keys and configuration variables
- Ensure the backend is running on `localhost:8000` before starting the frontend

## Latest Commit

**`cd0b268`** by Krishna J — Merge branch 'main' of https://github.com/KrishnaJ0324/ur-tutor

_No tracked file changes in this commit._
