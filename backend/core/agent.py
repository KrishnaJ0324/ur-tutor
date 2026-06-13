"""
core/agent.py
-------------
The deepagents harness: a single Claude Haiku tutor that self-routes between the teach /
quiz / evaluate skills and drives the progress engine through tools.

Isolation:
- Conversation state is keyed by thread_id = "<user_id>:<session_id>" against an
  AsyncSqliteSaver checkpointer (durable, survives restarts).
- The agent's scratch workspace is a per-session StateBackend; durable per-user notes live
  under /memories/ in an AsyncSqliteStore namespaced to the authenticated user_id, so one
  user's files can never surface in another's run.

Lifecycle: init_agent() / close_agent() are called from the FastAPI lifespan so the async
SQLite connections live for the process. get_agent() returns the compiled graph.
"""
import re
from dataclasses import dataclass

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.sqlite.aio import AsyncSqliteStore

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import (
    CompositeBackend, FilesystemBackend, StateBackend, StoreBackend,
)

from config import settings
from core.llm import build_model
from tools.progress_tools import PROGRESS_TOOLS


@dataclass
class TutorContext:
    """Runtime context carried into the graph; user_id is set from the verified JWT."""
    user_id: str = "anon"


SYSTEM_PROMPT = """You are UR Tutor, an adaptive tutor that takes a learner through a topic \
incrementally and only certifies a topic as complete after a passing quiz.

You have three skills — read the relevant SKILL.md before acting:
- `teach`: plan a concept curriculum, confirm difficulty, teach ONE concept at a time, run a \
short comprehension check, and record mastery on success.
- `quiz`: generate the multiple-choice gating quiz (or focused practice) for a topic.
- `evaluate`: grade submitted quiz answers, compute the score, and record the result.

Routing (decide each turn from the latest message and current progress):
- The learner wants to learn / continue / gave a difficulty → teach.
- The learner asks for a quiz/test, or all concepts are mastered → quiz.
- The learner submitted answers to the quiz you just posed → evaluate.

Hard rules:
- Identify the topic from the learner's message and pass that exact topic name to every tool.
- Progress is authoritative in the tools, not in your head. Call `get_progress(topic)` to \
ground yourself before teaching or quizzing.
- A concept is mastered ONLY after a passed comprehension check (`record_concept_mastery`).
- A topic is COMPLETE ONLY when `record_quiz_result` returns status "complete" (it enforces \
score >= pass threshold AND all concepts mastered). Never announce completion otherwise.

DIFFICULTY GATE — required before any teaching of a new topic:
- When the learner names a topic, call `get_progress(topic)` first. If it is "not_started" \
and the learner has NOT stated a level (Beginner / Intermediate / Advanced) in this \
conversation, your ENTIRE reply must be: "Are you a Beginner, Intermediate, or Advanced \
learner?" — then STOP. Do not teach, do not create a curriculum, do not assume a level.
- Only after the learner states a level do you call `get_or_create_curriculum(topic, \
proposed_concepts, difficulty)` with that level, then teach the first concept.
- Never default to "beginner". The curriculum tool will refuse and tell you to ask if you \
call it without a real, learner-provided difficulty.
- Never teach a concept that is not in the topic's curriculum.

TURN DISCIPLINE — this is critical:
- Teach EXACTLY ONE concept per turn, then STOP and wait for the learner. Never teach two \
concepts, never "continue" to the next concept, and never dump the whole topic in one reply.
- A teaching turn is short: roughly 120–220 words — a brief explanation, ONE concrete \
example, and ONE short comprehension-check question. Then end your turn. Do not keep calling \
tools or writing after you have posed the check question.
- The only tools a teaching turn may call are `get_progress` and (on a brand-new topic) \
`get_or_create_curriculum`. Do NOT call `record_concept_mastery` in the same turn you teach \
a concept — mastery is recorded next turn, only after the learner answers the check correctly.
- Be warm and concise. Format in clean Markdown. End every teaching turn with the single \
check question and nothing after it.

INTERACTIVE CHOICE CARDS — emit these so the UI can render clickable options:
- When you ask the learner to pick from a fixed set of options, append, as the VERY LAST \
thing in your reply, one machine-readable block:
  [[CHOICES]]{"kind":"single","question":"<short prompt>","options":["opt1","opt2",...]}[[/CHOICES]]
- Use it for the difficulty gate:
  [[CHOICES]]{"kind":"single","question":"Select your level","options":["Beginner","Intermediate","Advanced"]}[[/CHOICES]]
- Use it for a quiz instead of writing the options as prose:
  [[CHOICES]]{"kind":"quiz","topic":"<topic>","questions":[{"q":"...","options":["A text","B text","C text","D text"]}, ...]}[[/CHOICES]]
- Rules for the block: valid one-line JSON, ALWAYS closed with [[/CHOICES]], nothing after \
it. Do not reveal quiz answers in the block. A short sentence of prose may precede it. Only \
emit a block when offering discrete choices — never for normal teaching or open questions.
"""

_SKILLS = ["/skills/teach/", "/skills/quiz/", "/skills/evaluate/"]

# Module-level handles populated by init_agent().
_agent = None
_saver: AsyncSqliteSaver | None = None
_saver_conn: aiosqlite.Connection | None = None
_store_conn: aiosqlite.Connection | None = None


def _build_backend() -> CompositeBackend:
    return CompositeBackend(
        default=StateBackend(),  # per-session scratch workspace (thread-scoped)
        routes={
            "/skills/": FilesystemBackend(root_dir=settings.SKILLS_DIR, virtual_mode=True),
            "/memories/": StoreBackend(namespace=lambda rt: (rt.context.user_id or "anon",)),
        },
    )


async def init_agent() -> None:
    """Open async SQLite connections, set up the checkpointer + store, build the agent."""
    global _agent, _saver, _saver_conn, _store_conn

    _saver_conn = await aiosqlite.connect(settings.CHECKPOINT_DB_PATH)
    saver = AsyncSqliteSaver(_saver_conn)
    await saver.setup()
    _saver = saver

    _store_conn = await aiosqlite.connect(settings.STORE_DB_PATH)
    store = AsyncSqliteStore(_store_conn)
    await store.setup()

    if not settings.ANTHROPIC_API_KEY:
        # Boot without the model so auth/progress endpoints still work; /chat will return
        # a clear error until ANTHROPIC_API_KEY is set in .env.
        _agent = None
        return

    _agent = create_deep_agent(
        model=build_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=PROGRESS_TOOLS,
        skills=_SKILLS,
        backend=_build_backend(),
        context_schema=TutorContext,
        checkpointer=saver,
        store=store,
        # /skills is shared, read-only — the agent must not edit its own instructions.
        permissions=[FilesystemPermission(operations=["write"], paths=["/skills/**"], mode="deny")],
    )


async def close_agent() -> None:
    global _agent, _saver, _saver_conn, _store_conn
    _agent = None
    _saver = None
    if _saver_conn is not None:
        await _saver_conn.close()
        _saver_conn = None
    if _store_conn is not None:
        await _store_conn.close()
        _store_conn = None


def get_agent():
    if _agent is None:
        raise RuntimeError(
            "Tutor agent unavailable. Set ANTHROPIC_API_KEY in backend/.env and restart."
        )
    return _agent


async def reset_thread(thread_id: str) -> None:
    """Delete one conversation thread's checkpoints (clears chat memory, not progress)."""
    if _saver is not None:
        await _saver.adelete_thread(thread_id)


# A machine-readable block the skills emit to render interactive option/quiz cards.
# We strip it from the human-readable transcript.
CHOICES_RE = re.compile(r"\[\[CHOICES\]\].*?\[\[/CHOICES\]\]", re.DOTALL)


def _message_text(message) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    parts: list[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
    return "".join(parts)


async def get_history(thread_id: str) -> list[dict]:
    """Return the user/assistant transcript for a thread (markers stripped) for UI reload."""
    if _agent is None:
        return []
    state = await _agent.aget_state({"configurable": {"thread_id": thread_id}})
    messages = (state.values or {}).get("messages", []) if state else []
    out: list[dict] = []
    for m in messages:
        role = getattr(m, "type", None)
        if role == "human":
            text = _message_text(m).strip()
            if text:
                out.append({"role": "user", "content": text})
        elif role == "ai":
            text = CHOICES_RE.sub("", _message_text(m)).strip()
            if text:
                out.append({"role": "assistant", "content": text})
    return out
