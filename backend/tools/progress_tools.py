"""
tools/progress_tools.py
-----------------------
The deterministic tools the tutor agent calls to read and advance progress. They are the
ONLY way the agent touches the authoritative progress tables — the completion gate lives
in db/progress.py, so the model cannot "decide" a topic is complete on its own.

The authenticated user id is read from the active RunnableConfig (`configurable.user_id`),
which the /chat endpoint sets from the verified JWT — never from model input.
"""
import json

from langchain_core.runnables.config import ensure_config
from langchain_core.tools import tool

from db import progress
from db.base import SessionLocal


def _uid() -> int:
    cfg = ensure_config()
    uid = (cfg.get("configurable") or {}).get("user_id")
    if uid is None:
        raise ValueError("No authenticated user in context.")
    return int(uid)


def _json(data) -> str:
    return json.dumps(data, ensure_ascii=False)


VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}


@tool
def get_or_create_curriculum(topic: str, proposed_concepts: list[str],
                             difficulty: str = "") -> str:
    """Register (idempotently) the concept curriculum for a topic and return current progress.

    Call this once when the user starts a NEW topic, passing 4-8 ordered concept names you
    intend to teach. If the topic already exists, the stored curriculum is returned unchanged.

    Difficulty is REQUIRED and must come from the learner — it must be one of
    "beginner", "intermediate", or "advanced". If you don't have it yet, do NOT call this
    tool: ask the learner for their level first. If you call it without a valid difficulty,
    no curriculum is created and you'll get a directive to ask.

    Args:
        topic: The topic name, e.g. "Python loops".
        proposed_concepts: Ordered list of concept names to teach.
        difficulty: "beginner" | "intermediate" | "advanced" — REQUIRED, from the learner.
    Returns: JSON with topic status, percent, and the authoritative concept list.
    """
    d = (difficulty or "").strip().lower()
    if d not in VALID_DIFFICULTIES:
        return _json({
            "error": "difficulty_required",
            "instruction": (
                "You must know the learner's level before starting a topic. Ask exactly: "
                "'Are you a Beginner, Intermediate, or Advanced learner?' and STOP your turn. "
                "Do not teach, do not assume a level. Call this tool again only after the "
                "learner states their difficulty."
            ),
        })
    session = SessionLocal()
    try:
        return _json(progress.set_curriculum(session, _uid(), topic, proposed_concepts, d))
    finally:
        session.close()


@tool
def record_concept_mastery(topic: str, concept: str) -> str:
    """Mark ONE concept as mastered after the learner passes its comprehension check.

    Only call this once the learner has demonstrably understood the concept (answered a
    quick check correctly). Returns updated JSON progress (percent recomputed).
    """
    session = SessionLocal()
    try:
        return _json(progress.record_concept_mastery(session, _uid(), topic, concept))
    finally:
        session.close()


@tool
def record_quiz_result(topic: str, score_fraction: float) -> str:
    """Record a graded quiz attempt for a topic and apply the completion gate.

    Args:
        topic: The topic name.
        score_fraction: Fraction correct, 0.0-1.0 (e.g. 2 of 3 correct = 0.67).
    The topic becomes "complete" ONLY if score_fraction >= the pass threshold AND every
    concept is mastered; otherwise it stays "in_progress". Returns JSON including
    last_quiz_passed, pass_threshold, and a human-readable note.
    """
    session = SessionLocal()
    try:
        return _json(progress.record_quiz_result(session, _uid(), topic, score_fraction))
    finally:
        session.close()


@tool
def get_progress(topic: str) -> str:
    """Return current JSON progress for a topic: status, percent, and per-concept mastery.

    Use this to ground yourself before teaching/quizzing so you don't repeat mastered
    concepts or quiz before the curriculum is covered.
    """
    session = SessionLocal()
    try:
        return _json(progress.summarize(session, _uid(), topic))
    finally:
        session.close()


PROGRESS_TOOLS = [
    get_or_create_curriculum,
    record_concept_mastery,
    record_quiz_result,
    get_progress,
]
