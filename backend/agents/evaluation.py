"""
agents/evaluation.py
--------------------
This is the Grader AI Agent.
When a user submits a quiz answer, the router intercepts it and sends it here. 
This agent uses mathematical strictness to grade the submission against the active quiz keys stored in the State,
assigns fractional points, and returns an overarching critique for the user's progress.
"""

import logging
from langchain.agents import create_agent
from langchain_core.tools.simple import Tool
from langchain_core.messages import AIMessage
from core.llm import llm_strict
from core.state import GraphState

logger = logging.getLogger(__name__)

def verify_grading_accuracy(is_quiz: bool) -> str:
    """Invoked autonomously by the Evaluation Sub-Agent to determine the strictness level of the grading rubric dynamically."""
    if is_quiz:
        return "RUBRIC TOOL TARGET: Grade severely algorithmically and mathematically. Assess errors as sharp fractional point losses."
    return "RUBRIC TOOL TARGET: Grade completely conversationally. Maintain a highly nurturing tone and ignore minor spelling issues entirely."

grading_tool = Tool(
    name="verify_grading_accuracy",
    func=verify_grading_accuracy,
    description="Determine the strictness level of the grading rubric dynamically."
)

def eval_node(state: GraphState) -> dict:
    profile = state["profile"]
    messages = state["messages"]
    expected_answer = profile.get("last_question", "")
    is_quiz = expected_answer.startswith("QUIZ_KEY:")

    logger.info("eval_node invoked | is_quiz=%s", is_quiz)
    logger.debug("eval_node expected_answer=%r", expected_answer)

    system_prompt = """You are an expert AI tutor evaluating a student's answer(s). Return the evaluation strictly matching the output schema.\n\nCRITICAL INSTRUCTIONS:\n1. If the 'Expected Answer' contains a 'QUIZ_KEY' with multiple questions:\n   - Grade each question individually as strictly RIGHT or WRONG.\n   - Calculate the `accuracy` score as a strict mathematical decimal fraction of correct answers (e.g., 2 out of 3 correct = 0.67. 3 out of 3 = 1.0. 1 out of 2 = 0.5).\n   - In your `feedback` field, you MUST explain WHY they were right or wrong for EVERY single question. Provide the logical reason the correct option is the best one.\n   - Set `is_correct` to true ONLY if they got all questions right, or a strong passing grade (e.g., >= 0.70).\n2. If it is a standard single question (not a quiz):\n   - Evaluate their understanding conceptually. `accuracy` should be a float from 0.0 to 1.0.\n   - Provide standard, encouraging feedback explaining the concept.\n"""

    agent = create_agent(
        model=llm_strict,
        tools=[grading_tool],
        system_prompt=system_prompt
    )

    try:
        result = agent.invoke({
            "messages": messages,
            "expected_answer": expected_answer,
            "is_quiz": is_quiz
        })
    except Exception:
        logger.exception("eval_node agent invocation failed")
        raise

    text = result.content if hasattr(result, "content") else str(result)

    logger.info("eval_node complete | response_len=%d", len(text))

    # Optionally update profile as before (simple logic)
    profile["last_question"] = ""
    if is_quiz:
        profile["active_quiz"] = None

    return {
        "messages": [AIMessage(content=text)],
        "profile": profile,
        "output_response": text
    }
