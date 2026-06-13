"""
db/base.py
----------
SQLAlchemy engine + session factory for the application database (urtutor.db).
This holds the AUTHORITATIVE records: users and learning progress. The agent's
conversation state and scratch workspace live in separate SQLite files
(checkpoints.db / agent_store.db) managed by LangGraph.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

engine = create_engine(
    f"sqlite:///{settings.APP_DB_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    """Create all tables. Safe to call repeatedly (idempotent)."""
    import db.models  # noqa: F401 — register models on Base before create_all
    Base.metadata.create_all(bind=engine)


def get_session():
    """FastAPI dependency that yields a DB session and always closes it."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
