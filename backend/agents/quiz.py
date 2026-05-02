"""
agents/quiz.py
--------------
This is the specialized Tester AI Agent.
When the traffic cop router detects the user wants to practice, it bypasses conversational AI entirely 
and forces the LLM to output a strict `QuizResponse` JSON block containing exactly 4 randomized multiple-choice 
questions about the topic they just learned.
"""

from langchain.agents import create_agent
from langchain_core.tools.simple import Tool
from langchain_core.messages import AIMessage
from core.llm import llm_strict
from core.state import GraphState

def fetch_difficulty_guidelines(difficulty: str) -> str:
    """Tool utilized autonomously by the Quiz Sub-Agent to fetch standard academic guidelines dynamically based on learner difficulty."""
    if difficulty.lower() == "advanced":
        return "Guideline: Use highly complex, multi-step scenario questions with dense edge cases."
    elif difficulty.lower() == "intermediate":
        return "Guideline: Test applied logic, formulas, and real-world implementations."
    return "Guideline: Keep vocabulary simple and focus strictly on introductory taxonomy."

quiz_tool = Tool(
    name="fetch_difficulty_guidelines",
    func=fetch_difficulty_guidelines,
    description="Fetch academic guidelines based on learner difficulty."
)

def quiz_node(state: GraphState) -> dict:
    profile = state["profile"]
    messages = state["messages"]
    topic = profile.get("current_topic", "General")
    concept = profile.get("current_concept", "Review")
    difficulty = profile.get("difficulty", "easy")

    system_prompt = """You are a Quiz Generator for an AI tutoring system. Your HIGHEST PRIORITY is to generate a quiz on the EXACT topic the user requests in their latest message.\n\nSTRICT RULES:\n1. Every single question MUST directly test knowledge of the chosen concept.\n2. Each question MUST have exactly 4 options.\n3. Generate 2-3 questions at the specified difficulty based strictly on your Tool Guidelines.\n4. The answer field must contain the full correct answer text.\n5. In your response output, set the `topic` and `concept` fields to exactly what you are quizzing them on.\n"""

    agent = create_agent(
        model=llm_strict,
        tools=[quiz_tool],
        system_prompt=system_prompt
    )

    result = agent.invoke({
        "messages": messages,
        "topic": topic,
        "concept": concept,
        "difficulty": difficulty
    })

    text = result.content if hasattr(result, "content") else str(result)

    profile["current_topic"] = topic
    profile["current_concept"] = concept

    return {
        "messages": [AIMessage(content=text)],
        "profile": profile,
        "output_response": text
    }