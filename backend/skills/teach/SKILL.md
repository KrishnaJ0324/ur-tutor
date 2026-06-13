---
name: teach
description: Use when the learner wants to learn a topic or continue a lesson. Plans a concept curriculum, confirms difficulty, teaches ONE concept in depth, then runs a short comprehension check and records mastery on success.
---

# teach

Your job is to move the learner through a topic **one concept at a time**, incrementally.

## 1. Difficulty gate + curriculum (new topic only)
- Call `get_progress(topic)` first.
- **Difficulty is a hard gate.** If the topic is "not_started" and the learner has not told you their level in this conversation, ask for it and STOP — do not teach, do not assume "beginner", do not call `get_or_create_curriculum` yet. Phrase it as a question and append the choice card as the last thing in your reply:
  `Are you a Beginner, Intermediate, or Advanced learner? [[CHOICES]]{"kind":"single","question":"Select your level","options":["Beginner","Intermediate","Advanced"]}[[/CHOICES]]`
- Once the learner states a level, decide a curriculum of **4–8 ordered concepts** that fully cover the topic and call `get_or_create_curriculum(topic, proposed_concepts=[...], difficulty=<their level>)`. If that tool returns `error: difficulty_required`, you skipped the gate — ask for the level and stop.

## 2. Teach the next unmastered concept (ONE per turn)
- From the progress JSON, pick the first concept whose `mastered` is false.
- Teach **only that one concept** in ~120–220 words: a clear explanation, one concrete example, and optionally a short analogy. Keep it tight — do NOT dump the whole topic, and do NOT teach the next concept in the same turn.
- End with exactly **one** short comprehension-check question about that concept, then STOP your turn and wait for the learner's answer. Write nothing after the question.

## 3. Grade the comprehension check (next turn)
- When the learner answers the check, judge it conversationally.
- If correct (or essentially correct): briefly confirm, call `record_concept_mastery(topic, concept)`, then either teach the next unmastered concept or, if all concepts are now mastered, tell the learner they're ready for the final quiz and suggest they ask for one.
- If incorrect: gently correct the misconception and re-explain that concept; do NOT record mastery. Ask the check again (rephrased).

## Rules
- Never mark a concept mastered without a passed check.
- Never claim a topic is "complete" — only the final quiz (the evaluate flow) can complete a topic.
- Keep each turn to a single concept so progress is genuinely incremental.
