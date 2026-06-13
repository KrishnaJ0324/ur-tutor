"""
api/routes.py
-------------
Authenticated learning endpoints. Identity comes from the JWT (get_current_user) — the
client never names the user. /chat streams real Claude tokens from the deep agent; /progress
exposes the authoritative mastery records that drive the UI.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from core.agent import TutorContext, get_agent, get_history, reset_thread
from db import progress
from db import sessions as sessions_repo
from db.base import get_session
from db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: str


class ResetRequest(BaseModel):
    session_id: str


def _thread_id(user: User, session_id: str) -> str:
    return f"{user.id}:{session_id or 'main'}"


def _extract_text(chunk) -> str:
    """Pull human-visible text out of an assistant token chunk (skip tool-call deltas)."""
    if not isinstance(chunk, AIMessageChunk):
        return ""
    content = chunk.content
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


@router.post("/chat", tags=["Tutor"])
async def chat_endpoint(req: ChatMessage, user: User = Depends(get_current_user),
                        session: Session = Depends(get_session)):
    # Ensure the session row exists, bump it to the top, and title it from the first message.
    cs = sessions_repo.ensure(session, user.id, req.session_id)
    sessions_repo.touch(session, cs, first_user_message=req.message)

    thread_id = _thread_id(user, req.session_id)
    config = {"configurable": {"thread_id": thread_id, "user_id": user.id}}
    context = TutorContext(user_id=str(user.id))
    payload = {"messages": [{"role": "user", "content": req.message}]}

    logger.info("chat | user=%s thread=%s len=%d", user.id, thread_id, len(req.message or ""))

    async def token_stream():
        try:
            agent = get_agent()  # raises a clear error if OPENROUTER_API_KEY is unset
            async for chunk, _meta in agent.astream(
                payload, config=config, context=context, stream_mode="messages"
            ):
                text = _extract_text(chunk)
                if text:
                    yield text
        except Exception as exc:  # surface model/agent errors to the client gracefully
            logger.exception("chat stream failed | user=%s", user.id)
            yield f"\n\n⚠️ **Backend error:** {exc}"

    return StreamingResponse(token_stream(), media_type="text/plain")


@router.post("/sessions", tags=["Sessions"])
def create_session(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    cs = sessions_repo.create(session, user.id)
    return sessions_repo.as_dict(cs)


@router.get("/sessions", tags=["Sessions"])
def list_sessions(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return {"sessions": [sessions_repo.as_dict(cs) for cs in sessions_repo.list_for_user(session, user.id)]}


@router.get("/sessions/{sid}/messages", tags=["Sessions"])
async def session_messages(sid: str, user: User = Depends(get_current_user),
                           session: Session = Depends(get_session)):
    if sessions_repo.get(session, user.id, sid) is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"messages": await get_history(_thread_id(user, sid))}


@router.delete("/sessions/{sid}", tags=["Sessions"])
async def delete_session(sid: str, user: User = Depends(get_current_user),
                         session: Session = Depends(get_session)):
    if not sessions_repo.delete(session, user.id, sid):
        raise HTTPException(status_code=404, detail="Session not found")
    await reset_thread(_thread_id(user, sid))  # also clear the conversation checkpoints
    return {"status": "deleted"}


@router.get("/progress", tags=["Tutor"])
def all_progress(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return {"topics": progress.list_progress(session, user.id)}


@router.get("/progress/{topic}", tags=["Tutor"])
def topic_progress(topic: str, user: User = Depends(get_current_user),
                   session: Session = Depends(get_session)):
    return progress.summarize(session, user.id, topic)


@router.post("/session/reset", tags=["Tutor"])
async def reset_session(req: ResetRequest, user: User = Depends(get_current_user)):
    """Clear the conversation memory for one of the user's sessions (progress is preserved)."""
    await reset_thread(_thread_id(user, req.session_id))
    logger.info("reset session | user=%s session=%s", user.id, req.session_id)
    return {"status": "reset"}
