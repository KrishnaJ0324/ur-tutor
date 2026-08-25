"""
api/routes.py
-------------
Authenticated learning endpoints. Identity comes from the JWT (get_current_user) — the
client never names the user. /chat streams real Claude tokens from the deep agent; /progress
exposes the authoritative mastery records that drive the UI.

Bring-your-own-key: /chat also requires the caller's own Anthropic API key in the
X-Anthropic-Key header. The key is used for that request only and is never persisted.
"""
import logging

import anthropic
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from config import settings
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


class ApiKeyRequest(BaseModel):
    api_key: str


# Returned when the caller has not supplied an Anthropic API key. 428 (rather than 400)
# lets the frontend tell "you need to add a key" apart from any other bad request.
NO_KEY_STATUS = status.HTTP_428_PRECONDITION_REQUIRED


def get_api_key(x_anthropic_key: str = Header(default="")) -> str:
    """Pull the caller's own Anthropic API key off the request."""
    key = (x_anthropic_key or "").strip()
    if not key:
        raise HTTPException(
            status_code=NO_KEY_STATUS,
            detail="Add your Anthropic API key to start chatting.",
        )
    return key


def _thread_id(user: User, session_id: str) -> str:
    return f"{user.id}:{session_id or 'main'}"


def _friendly_error(exc: BaseException) -> str:
    """Map a model/agent failure to a message that is safe to show the learner.

    Raw exception text is never sent to the browser: it can carry request internals, and
    the full detail is already in the server log. Errors arrive wrapped by LangChain as
    often as not, so walk the cause chain looking for the underlying Anthropic error.
    """
    seen: list[BaseException] = []
    cur: BaseException | None = exc
    while cur is not None and not any(cur is prev for prev in seen):
        seen.append(cur)
        if isinstance(cur, anthropic.AuthenticationError):
            return "Your Anthropic API key was rejected. Add a valid key and try again."
        if isinstance(cur, anthropic.PermissionDeniedError):
            return "Your Anthropic API key does not have access to this model."
        if isinstance(cur, anthropic.RateLimitError):
            return "Anthropic is rate-limiting this key. Wait a moment and try again."
        if isinstance(cur, anthropic.BadRequestError):
            if "credit balance" in str(cur).lower():
                return "This Anthropic key has no credit left. Top it up and try again."
            return "Anthropic rejected the request."
        if isinstance(cur, anthropic.APIConnectionError):
            return "Could not reach Anthropic. Check your connection and try again."
        cur = cur.__cause__ or cur.__context__
    return "Something went wrong on the tutor's side. Please try again."


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
                        api_key: str = Depends(get_api_key),
                        session: Session = Depends(get_session)):
    # Ensure the session row exists and bump it to the top. The title is set later, from the
    # topic the tutor teaches (see get_or_create_curriculum), not from the first message.
    cs = sessions_repo.ensure(session, user.id, req.session_id)
    sessions_repo.touch(session, cs)

    thread_id = _thread_id(user, req.session_id)
    config = {"configurable": {"thread_id": thread_id, "user_id": user.id}}
    context = TutorContext(user_id=str(user.id))
    payload = {"messages": [{"role": "user", "content": req.message}]}

    logger.info("chat | user=%s thread=%s len=%d", user.id, thread_id, len(req.message or ""))

    async def token_stream():
        try:
            agent = get_agent(api_key)  # compiled per key, cached
            async for chunk, _meta in agent.astream(
                payload, config=config, context=context, stream_mode="messages"
            ):
                text = _extract_text(chunk)
                if text:
                    yield text
        except Exception as exc:  # surface model/agent errors to the client gracefully
            logger.exception("chat stream failed | user=%s", user.id)
            yield f"\n\n⚠️ {_friendly_error(exc)}"

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


@router.post("/key/validate", tags=["Tutor"])
async def validate_key(req: ApiKeyRequest, user: User = Depends(get_current_user)):
    """Check an Anthropic API key before the frontend saves it.

    Uses the Models endpoint: it verifies the credential without spending any tokens.
    The key is not stored — the client keeps it and sends it with each chat request.
    """
    key = (req.api_key or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key is required.")

    client = anthropic.AsyncAnthropic(api_key=key, base_url=settings.ANTHROPIC_BASE_URL)
    try:
        await client.models.list(limit=1)
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=400, detail="That API key was rejected by Anthropic.")
    except anthropic.PermissionDeniedError:
        raise HTTPException(status_code=400, detail="That API key lacks access to the Claude API.")
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Anthropic: {exc}")
    finally:
        await client.close()

    return {"valid": True, "model": settings.MODEL_NAME}
