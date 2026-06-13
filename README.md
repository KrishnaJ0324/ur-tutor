# UR Tutor

An adaptive AI tutoring system where you learn a topic **one concept at a time** and a topic is only marked **complete after you pass its quiz**. It is built on a [`deepagents`](https://pypi.org/project/deepagents/) harness running **Anthropic Claude Haiku 4.5**, with per-user accounts, isolated multi-session chat, skills-driven teaching, and a mastery-gated progress engine.

**Checkout the website:** https://urtutor.netlify.app/

**Version:** `3.0.0`

---

## How it works

1. **You pick a topic.** The tutor first asks your level (**Beginner / Intermediate / Advanced**) — a hard gate; nothing is taught until you choose.
2. **It builds a curriculum** of 4–8 concepts and teaches **one concept per turn**, ending each turn with a short comprehension check.
3. **Mastery is earned, not assumed.** A concept is marked *mastered* only after you pass its check. Progress % = concepts mastered ÷ total.
4. **The quiz is the gate.** When you ask for / are ready for the quiz, the tutor generates multiple-choice questions. The topic flips to **complete only when you score ≥ the pass threshold (default 80%) AND every concept is mastered** — enforced in code, not by the model.

The difficulty prompt and the quiz render as **interactive choice cards** above the chat box (click to answer; quizzes are paginated).

### Architecture

```
React (Vite) ──HTTPS/JWT──> FastAPI
                              ├─ Auth (OAuth2 password + JWT)
                              ├─ Deep agent harness (deepagents + Claude Haiku 4.5)
                              │    ├─ skills: teach / quiz / evaluate  (SKILL.md files)
                              │    ├─ progress tools  (curriculum, mastery, quiz gate)
                              │    └─ CompositeBackend: StateBackend (per-session scratch)
                              │                         + StoreBackend /memories (per-user)
                              ├─ Checkpointer: AsyncSqliteSaver  (conversation state)
                              └─ Authoritative records: SQLite (users, topics, concepts, quizzes, sessions)
```

**Isolation:** identity comes from the verified JWT (never the client). Conversation state is keyed by `thread_id = "<user_id>:<session_id>"`; durable agent memory is namespaced to the authenticated user. One user's data can never surface in another's session.

---

## Tech stack

**Backend:** FastAPI · deepagents · LangChain / LangGraph · `langchain-openai` (Claude Haiku 4.5) · `langgraph-checkpoint-sqlite` · SQLAlchemy · python-jose (JWT) · bcrypt
**Frontend:** React 19 · TypeScript · Vite · react-markdown · lucide-react · tsparticles

---

## Project layout

```
backend/
  main.py                 FastAPI app, lifespan, CORS
  config.py               settings from environment
  auth/                   security (bcrypt + JWT), deps, register/login/me routes
  core/
    llm.py                ChatOpenAI(anthropic/claude-haiku-4.5)
    agent.py              deep-agent harness, backends, checkpointer/store, history
  tools/progress_tools.py agent tools that drive the progress engine
  skills/{teach,quiz,evaluate}/SKILL.md   on-demand tutor skills
  db/                     SQLAlchemy models + repos (users, progress, sessions)
  api/routes.py           /chat (streaming), /progress, /sessions
frontend/
  src/api/                authApi · tutorApi · sessionApi
  src/components/         Login · Chat · ChoiceCard · ProfileWidget
  src/App.tsx             auth gate + session sidebar + progress
```

---

## API

**Base URL (local):** `http://localhost:8000` · **Swagger:** `http://localhost:8000/docs`
**Auth:** OAuth2 password flow → JWT bearer token (use Swagger's **Authorize** button).

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/auth/register` | — | Create an account → returns a token |
| `POST` | `/auth/token` | — | Log in (form `username`/`password`) → token |
| `GET`  | `/auth/me` | ✅ | Current user |
| `POST` | `/chat` | ✅ | Streamed tutoring turn (`{message, session_id}`) |
| `GET`  | `/sessions` | ✅ | List the user's chat sessions |
| `POST` | `/sessions` | ✅ | Create a new chat session |
| `GET`  | `/sessions/{id}/messages` | ✅ | Transcript for a session |
| `DELETE` | `/sessions/{id}` | ✅ | Delete a session + its conversation |
| `GET`  | `/progress` | ✅ | All topics with status + percent |
| `GET`  | `/progress/{topic}` | ✅ | One topic's progress |
| `POST` | `/session/reset` | ✅ | Clear one session's chat memory (progress kept) |
| `GET`  | `/health` | — | Health check |

`/chat` returns a `text/plain` token stream. The tutor may append an interactive block — `[[CHOICES]]{...}[[/CHOICES]]` — which the frontend renders as a choice/quiz card and strips from the visible text.

---

## Local development

**Prerequisites:** Python 3.12, Node.js 18+, an API key with access to `anthropic/claude-haiku-4.5`.

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn main:app --reload --port 8000
```


### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev         
```
---

## Notes

- Registration is currently open and every `/chat` call consumes API credits — add rate limiting / an invite gate before exposing it publicly.
