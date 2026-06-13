# UR Tutor

An adaptive AI tutoring system where you learn a topic **one concept at a time** and a topic is only marked **complete after you pass its quiz**. It is built on a [`deepagents`](https://pypi.org/project/deepagents/) harness running **Claude Haiku 4.5 via [OpenRouter](https://openrouter.ai/)**, with per-user accounts, isolated multi-session chat, skills-driven teaching, and a mastery-gated progress engine.

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
                              ├─ Deep agent harness (deepagents + Claude Haiku 4.5 via OpenRouter)
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

**Backend:** FastAPI · deepagents · LangChain / LangGraph · `langchain-openai` (Claude Haiku 4.5 via OpenRouter) · `langgraph-checkpoint-sqlite` · SQLAlchemy · python-jose (JWT) · bcrypt
**Frontend:** React 19 · TypeScript · Vite · react-markdown · lucide-react · tsparticles

---

## Project layout

```
backend/
  main.py                 FastAPI app, lifespan, CORS
  config.py               settings from environment
  auth/                   security (bcrypt + JWT), deps, register/login/me routes
  core/
    llm.py                ChatOpenAI(anthropic/claude-haiku-4.5) via OpenRouter
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

**Prerequisites:** Python 3.12, Node.js 18+, an [OpenRouter](https://openrouter.ai/) API key with access to `anthropic/claude-haiku-4.5`.

### Backend

```bash
cd backend
pip install -r requirements.txt
# create .env (see Environment variables below) with at least OPENROUTER_API_KEY and JWT_SECRET
python -m uvicorn main:app --reload --port 8000
```

The app boots even without `OPENROUTER_API_KEY` (auth and progress work; `/chat` returns a clear error until the key is set).

### Frontend

```bash
cd frontend
npm install
# optional: cp .env.example .env.local  (defaults to http://localhost:8000)
npm run dev          # http://localhost:5173
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Default | Notes |
|---|---|---|---|
| `OPENROUTER_API_KEY` | ✅ | — | OpenRouter key with access to Claude Haiku 4.5 |
| `JWT_SECRET` | ✅ | insecure dev value | Long random string; **stable** (changing it invalidates all logins) |
| `OPENROUTER_BASE_URL` | | `https://openrouter.ai/api/v1` | OpenRouter's OpenAI-compatible endpoint |
| `MODEL_NAME` | | `anthropic/claude-haiku-4.5` | OpenRouter model slug |
| `MODEL_MAX_TOKENS` | | `8000` | |
| `PASS_THRESHOLD` | | `0.8` | Quiz pass mark for topic completion |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | `1440` | |
| `FRONTEND_URL` | | `http://localhost:5173` | Exact allowed origin(s); comma-separated for multiple |
| `CORS_ORIGIN_REGEX` | | localhost + `*.vercel.app` + `*.netlify.app` | Extra allowed origins (covers preview deploys) |
| `APP_DB_PATH` / `CHECKPOINT_DB_PATH` / `STORE_DB_PATH` | | files under `backend/` | Point at a persistent disk in production |

Generate a secret: `python -c "import secrets;print(secrets.token_urlsafe(48))"`

### Frontend (build-time, must be `VITE_`-prefixed)

| Variable | Default | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL. **Baked in at build time** — set before building and redeploy to change. |

---

## Deployment (split: Netlify + Render)

**Frontend → Netlify**
- Base directory `frontend`, build `npm run build`, publish `dist`.
- Set `VITE_API_BASE_URL` to your backend URL, then **Clear cache and deploy** (Vite inlines it at build time).

**Backend → Render (Web Service)**
- Root directory `backend`; build `pip install -r requirements.txt`; start `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Env: `OPENROUTER_API_KEY`, `JWT_SECRET`, `PYTHON_VERSION=3.12.6`. Optionally `FRONTEND_URL` (your Netlify URL) — the default `CORS_ORIGIN_REGEX` already allows `*.netlify.app` / `*.vercel.app`.
- Run a **single worker** (don't use `--workers`) — the SQLite checkpointer/store is single-instance.

> **Persistence caveat:** on Render's free tier the filesystem is **ephemeral** — the SQLite databases (users, progress, conversations) are wiped on every redeploy and on cold starts after idle. For durable data, use a paid instance with a persistent disk (point the `*_DB_PATH` vars at it) or migrate to PostgreSQL.

CORS is HTTPS-aware and serves both platforms; the frontend must call the backend over `https://` (no mixed content).

---

## Notes

- Registration is currently open and every `/chat` call consumes OpenRouter credits — add rate limiting / an invite gate before exposing it publicly.
- `*.db` and `.env` files are gitignored; never commit them.
