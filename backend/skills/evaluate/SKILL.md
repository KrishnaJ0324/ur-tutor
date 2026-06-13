---
name: evaluate
description: Use when the learner submits answers to a quiz that was just posed. Grades each answer right/wrong, computes the score fraction, gives per-question feedback, and records the result so the completion gate is applied.
---

# evaluate

Grade the learner's submitted quiz answers for the most recent quiz on a topic.

The submission arrives as text listing the learner's chosen option for each question (the UI
sends one line per question, e.g. `1. <chosen option text>`). Match by question number.

## Grading
- Match each submitted answer against the correct option for that question.
- Mark every question strictly **right or wrong**.
- Compute `score_fraction = correct / total` (e.g. 4 of 5 correct = 0.8).

## Feedback
- For **every** question, state right/wrong and explain *why* the correct option is correct.
- Be encouraging but accurate.

## Record the result (required)
- Call `record_quiz_result(topic, score_fraction)`. This applies the gate:
  - The topic becomes **complete** only if `score_fraction >= pass_threshold` (default 0.8) AND all concepts are mastered.
  - Otherwise it stays **in progress**.
- Read the JSON the tool returns and relay its outcome honestly:
  - If completed: congratulate the learner — the topic is done.
  - If passed but not all concepts mastered: say what's left to master.
  - If failed: report the score vs the threshold, identify the weakest concepts, and offer to reteach them before another quiz. Do not record mastery here.
- Never announce completion unless `record_quiz_result` returned status "complete".
