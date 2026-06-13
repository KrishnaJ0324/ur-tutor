"""
db/progress.py
--------------
The mastery-gated progress engine — the authoritative source of truth for "how far
through a topic is this user". All completion logic lives here (deterministic Python),
never in the model.

Key rule (enforced in `record_quiz_result`):
    A topic flips to `complete` ONLY when a quiz scores >= the topic's pass_threshold
    AND every concept in its curriculum is mastered. Otherwise it stays `in_progress`.

`percent` always reflects concepts mastered / total concepts (0..100).
"""
from sqlalchemy.orm import Session

from db.models import Concept, QuizAttempt, Topic


# ----- internal helpers -----------------------------------------------------

def _recompute_percent(topic: Topic) -> None:
    total = len(topic.concepts)
    if total == 0:
        topic.percent = 0
        return
    mastered = sum(1 for c in topic.concepts if c.mastered)
    topic.percent = round(100 * mastered / total)


def _all_mastered(topic: Topic) -> bool:
    return len(topic.concepts) > 0 and all(c.mastered for c in topic.concepts)


def get_or_create_topic(session: Session, user_id: int, name: str,
                        difficulty: str | None = None,
                        pass_threshold: float | None = None) -> Topic:
    name = name.strip()
    topic = (
        session.query(Topic)
        .filter(Topic.user_id == user_id, Topic.name.ilike(name))
        .first()
    )
    if topic is None:
        topic = Topic(user_id=user_id, name=name, difficulty=difficulty or "")
        if pass_threshold is not None:
            topic.pass_threshold = pass_threshold
        session.add(topic)
        session.commit()
        session.refresh(topic)
    elif difficulty and not topic.difficulty:
        topic.difficulty = difficulty
        session.commit()
    return topic


# ----- public API (used by tools + REST) ------------------------------------

def set_curriculum(session: Session, user_id: int, topic_name: str,
                   concepts: list[str], difficulty: str | None = None) -> dict:
    """Create the concept list for a topic the first time it's taught (idempotent)."""
    topic = get_or_create_topic(session, user_id, topic_name, difficulty)
    existing = {c.name.lower() for c in topic.concepts}
    ordinal = len(topic.concepts)
    for name in concepts:
        name = name.strip()
        if name and name.lower() not in existing:
            session.add(Concept(topic_id=topic.id, name=name, ordinal=ordinal))
            existing.add(name.lower())
            ordinal += 1
    session.commit()
    session.refresh(topic)
    _recompute_percent(topic)
    session.commit()
    return summarize(session, user_id, topic_name)


def record_concept_mastery(session: Session, user_id: int, topic_name: str,
                           concept_name: str) -> dict:
    """Mark a concept mastered after a passed comprehension check; recompute percent."""
    topic = get_or_create_topic(session, user_id, topic_name)
    concept = (
        session.query(Concept)
        .filter(Concept.topic_id == topic.id, Concept.name.ilike(concept_name.strip()))
        .first()
    )
    if concept is None:
        # Tolerate a concept the agent names that wasn't in the seeded curriculum.
        concept = Concept(topic_id=topic.id, name=concept_name.strip(),
                          ordinal=len(topic.concepts), mastered=True)
        session.add(concept)
    else:
        concept.mastered = True
    session.commit()
    session.refresh(topic)
    _recompute_percent(topic)
    session.commit()
    return summarize(session, user_id, topic_name)


def record_quiz_result(session: Session, user_id: int, topic_name: str,
                       score: float) -> dict:
    """Record a quiz attempt and apply the completion gate."""
    score = max(0.0, min(1.0, float(score)))
    topic = get_or_create_topic(session, user_id, topic_name)
    passed = score >= topic.pass_threshold
    session.add(QuizAttempt(topic_id=topic.id, score=score, passed=passed))

    if passed and _all_mastered(topic):
        topic.status = "complete"
        topic.percent = 100
    else:
        topic.status = "in_progress"
        _recompute_percent(topic)
    session.commit()

    result = summarize(session, user_id, topic_name)
    result["last_quiz_score"] = round(score, 2)
    result["last_quiz_passed"] = passed
    result["pass_threshold"] = topic.pass_threshold
    if passed and not _all_mastered_by_name(session, topic.id):
        result["note"] = ("Quiz passed, but not all concepts are mastered yet — "
                          "the topic stays in progress until every concept is mastered.")
    elif not passed:
        result["note"] = (f"Quiz scored {round(score*100)}% (need "
                          f"{round(topic.pass_threshold*100)}%). Topic stays in progress; "
                          "reteach the weak concepts and quiz again.")
    return result


def _all_mastered_by_name(session: Session, topic_id: int) -> bool:
    topic = session.get(Topic, topic_id)
    return _all_mastered(topic) if topic else False


def summarize(session: Session, user_id: int, topic_name: str) -> dict:
    topic = (
        session.query(Topic)
        .filter(Topic.user_id == user_id, Topic.name.ilike(topic_name.strip()))
        .first()
    )
    if topic is None:
        return {"topic": topic_name, "status": "not_started", "percent": 0, "concepts": []}
    return {
        "topic": topic.name,
        "difficulty": topic.difficulty,
        "status": topic.status,
        "percent": topic.percent,
        "pass_threshold": topic.pass_threshold,
        "concepts": [
            {"name": c.name, "mastered": c.mastered} for c in topic.concepts
        ],
    }


def list_progress(session: Session, user_id: int) -> list[dict]:
    topics = (
        session.query(Topic)
        .filter(Topic.user_id == user_id)
        .order_by(Topic.created_at)
        .all()
    )
    return [summarize(session, user_id, t.name) for t in topics]
