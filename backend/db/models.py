"""
db/models.py
------------
SQLAlchemy ORM models for the authoritative records.

- User            : an account (login).
- Topic           : something a user is learning; carries status + percent + pass threshold.
- Concept         : one unit within a topic's curriculum; `mastered` flips after a passed check.
- QuizAttempt     : one graded quiz on a topic; `passed` reflects the >= threshold gate.

A topic is only marked `complete` when a quiz attempt passes the threshold AND every
concept is mastered — enforced in db/progress.py, not by the model.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    """A named conversation. Its `id` is the session key in the LangGraph thread_id
    (`<user_id>:<session_id>`); the conversation transcript lives in the checkpointer."""
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)  # uuid hex
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, default="New chat")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="sessions")


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_topic"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    difficulty = Column(String, default="")
    status = Column(String, default="in_progress")  # in_progress | complete
    percent = Column(Integer, default=0)             # 0..100, concepts mastered / total
    pass_threshold = Column(Float, default=0.8)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="topics")
    concepts = relationship("Concept", back_populates="topic", cascade="all, delete-orphan",
                            order_by="Concept.ordinal")
    quiz_attempts = relationship("QuizAttempt", back_populates="topic", cascade="all, delete-orphan",
                                 order_by="QuizAttempt.created_at")


class Concept(Base):
    __tablename__ = "concepts"
    __table_args__ = (UniqueConstraint("topic_id", "name", name="uq_topic_concept"),)

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    ordinal = Column(Integer, default=0)
    mastered = Column(Boolean, default=False)

    topic = relationship("Topic", back_populates="concepts")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False)   # 0.0 .. 1.0
    passed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utcnow)

    topic = relationship("Topic", back_populates="quiz_attempts")
