# UR Tutor

## Overview

UR Tutor is an adaptive AI tutoring system that uses multi-agent workflows to teach, quiz, and evaluate students in real-time. Built on LangGraph with a React frontend, it orchestrates specialized teaching, quiz, and evaluation agents to deliver personalized learning experiences through conversational interactions.

## Key Modules

**Backend** — An adaptive AI tutoring engine built on LangGraph that orchestrates multi-agent workflows through a supervisor router. It dispatches user messages to specialized teaching, quiz, and evaluation agents, each enhanced with ReAct-style decision-making. The FastAPI-based infrastructure handles real-time streaming responses, LLM configuration with dual temperature settings for different task types, and in-memory state management. Google Gemini serves as the LLM backbone, and structured output enforcement ensures reliable data contracts between agents and the frontend for teaching materials, quiz questions, and grading rubrics.

**Frontend** — A modern React + TypeScript single-page application built with Vite that provides the user interface for UR Tutor. It features an interactive chat component for real-time tutoring conversations, a particle-animated background, profile tracking functionality, and a dark glassmorphic design language. The module streams responses from the backend API, manages user state, and leverages TypeScript and ESLint for code quality, with optimized development experience through Vite's hot module reloading.

**Root** — The foundational project configuration layer that establishes shared development practices for this hybrid Node.js and Python project. It provides a `.gitignore` configuration that excludes build artifacts, dependencies, and environment-specific files from version control while supporting a polyglot development environment across multiple language ecosystems.

## How It Works

When a user submits a message through the React frontend chat interface, it's sent to the FastAPI backend where a supervisor router agent receives and analyzes the request. Based on the message content, the router dispatches the query to one of three specialized agents: a teaching agent for explanations and learning materials, a quiz agent for assessments, or an evaluation agent for grading and feedback. Each agent leverages Google Gemini as the underlying LLM with ReAct-style reasoning and tool invocation to autonomously break down problems and generate structured responses. The backend maintains conversation state in-memory via LangGraph, streams responses in real-time back to the frontend, and enforces strict schema validation to ensure reliable parsing and rendering of educational content.

## Getting Started

### Prerequisites
- Node.js (v16+) and npm
- Python 3.9+
- Google Gemini API key

### Installation

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY="your-api-key"
python -m uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Configuration
Create a `.env` file in the backend directory with your Google Gemini API key and desired LLM temperature settings for teaching and quiz modes.

### Running Locally
Start both the backend server (default: `http://localhost:8000`) and frontend dev server (default: `http://localhost:5173`). The frontend will automatically connect to the backend API and display the interactive tutoring interface.