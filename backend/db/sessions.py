"""
db/sessions.py
--------------
Repository for chat sessions (the conversations listed in the left panel). Each row's `id`
is the session key embedded in the LangGraph thread_id.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models import ChatSession

DEFAULT_TITLE = "New chat"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create(session: Session, user_id: int, title: str = DEFAULT_TITLE) -> ChatSession:
    cs = ChatSession(id=uuid.uuid4().hex, user_id=user_id, title=title)
    session.add(cs)
    session.commit()
    session.refresh(cs)
    return cs


def get(session: Session, user_id: int, sid: str) -> ChatSession | None:
    return (
        session.query(ChatSession)
        .filter(ChatSession.id == sid, ChatSession.user_id == user_id)
        .first()
    )


def list_for_user(session: Session, user_id: int) -> list[ChatSession]:
    return (
        session.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def ensure(session: Session, user_id: int, sid: str) -> ChatSession:
    """Return the session, creating it with the given id if it doesn't exist yet."""
    cs = get(session, user_id, sid)
    if cs is None:
        cs = ChatSession(id=sid, user_id=user_id, title=DEFAULT_TITLE)
        session.add(cs)
        session.commit()
        session.refresh(cs)
    return cs


def touch(session: Session, cs: ChatSession, first_user_message: str | None = None) -> None:
    """Bump updated_at; set a title from the first message if still untitled."""
    cs.updated_at = _utcnow()
    if first_user_message and cs.title == DEFAULT_TITLE:
        title = first_user_message.strip().splitlines()[0][:48]
        cs.title = title or DEFAULT_TITLE
    session.commit()


def delete(session: Session, user_id: int, sid: str) -> bool:
    cs = get(session, user_id, sid)
    if cs is None:
        return False
    session.delete(cs)
    session.commit()
    return True


def as_dict(cs: ChatSession) -> dict:
    return {
        "id": cs.id,
        "title": cs.title,
        "created_at": cs.created_at.isoformat() if cs.created_at else None,
        "updated_at": cs.updated_at.isoformat() if cs.updated_at else None,
    }
