---
name: quiz
description: Use when the learner asks for a quiz/test/practice, or when all concepts of a topic are mastered and it's time for the final gating quiz. Generates difficulty-appropriate multiple-choice questions covering the topic's concepts.
---

# quiz

Generate the **final gating quiz** for a topic (or focused practice on request).

## Before generating
- Call `get_progress(topic)` to see which concepts exist and their difficulty.
- The gating quiz should cover the topic's concepts (favor concepts that are mastered, since the quiz verifies retention across the whole topic).

## Question format
- Generate **4–6 multiple-choice questions**, each with **exactly 4 options**.
- Calibrate difficulty:
  - beginner → simple recall and definitions.
  - intermediate → applied reasoning and small scenarios.
  - advanced → multi-step / edge-case scenarios.
- Write a one-line intro (e.g. "Here's your quiz on <topic> — pick an answer for each question.").
- Then emit the quiz as an interactive choice card — the LAST thing in your reply, valid one-line JSON, closed with `[[/CHOICES]]`, nothing after it:

  `[[CHOICES]]{"kind":"quiz","topic":"<topic>","questions":[{"q":"<question text>","options":["<opt A>","<opt B>","<opt C>","<opt D>"]}, ...]}[[/CHOICES]]`

- Do **not** reveal the answers (not in the prose, not in the block). The UI renders the card and the learner submits their selections.
- Do NOT call any progress tool here. Recording the score happens during grading (evaluate).
