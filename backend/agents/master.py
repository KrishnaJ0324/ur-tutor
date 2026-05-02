"""
agents/master.py
----------------
This is the central Teacher AI Agent. 
It operates strictly via the Socratic method. If the router detects the user hasn't selected a difficulty, 
this agent halts and forces a prompt. Otherwise, it generates comprehensive textbook-style lessons 
and stops when a topic is fully addressed.
"""

from langchain.agents import create_agent
from langchain_core.tools.simple import Tool
from langchain_core.messages import AIMessage
from core.llm import llm
from core.state import GraphState

def get_pedagogical_fact(concept: str) -> str:
    """A formal LangChain tool that generates a fun trivia fact based on the concept to enrich the prompt."""
    facts = {
        "python": "Fun Fact: Python was named after Monty Python, not the snake!",
        "loops": "Fun Fact: The first computer loop was written by Ada Lovelace in 1843!",
        "math": "Fun Fact: A 'jiffy' is an actual unit of time measuring 1/100th of a second!"
    }
    for key in facts:
        if key in concept.lower():
            return facts[key]
    return "Fun Fact: Learning new things physically creates new neural pathways in your brain!"

pedagogical_tool = Tool(
    name="get_pedagogical_fact",
    func=get_pedagogical_fact,
    description="Get a fun trivia fact about a concept to enrich the lesson."
)

def teach_node(state: GraphState) -> dict:
    profile = state["profile"]
    user_message = state["messages"][-1].content

    # Compose the agent prompt
    system_prompt = """You are an expert AI tutor. Your HIGHEST PRIORITY is to teach the EXACT topic/concept the user asks for in their message.\n\nTEACHING RULES:\n- If the user asks to learn a NEW topic and you do NOT know their difficulty level yet (Difficulty is empty), you MUST set `needs_difficulty` to true and set `explanation` to \"Great! Before we dive in, are you a Beginner, Intermediate, or Advanced learner?\". Do NOT teach yet.\n- If the user provides a difficulty (e.g. \"I am a beginner\"), set `detected_difficulty` to \"beginner\", set `needs_difficulty` to false, and START teaching the actual topic.\n- Teach comprehensively. Cover the concept in depth before asking any quiz questions.\n- Set `is_topic_complete` to false while still teaching. Only set it to true when the full concept has been covered across multiple steps.\n- For early steps (steps 1-3), set `question` to null — just teach, don't quiz.\n- For later steps (step 4+), you may include a quick comprehension check question.\n- The `topic` and `concept` fields MUST match what you are teaching.\n\nTOPIC EXTRACTION (CRITICAL):\n- If the user's latest message explicitly mentions a topic, you MUST teach THAT topic.\n"""

    agent = create_agent(
        model=llm,
        tools=[pedagogical_tool],
        system_prompt=system_prompt
    )

    # Compose the input for the agent
    concept = profile.get("current_concept", "Basics")
    topic = profile.get("current_topic", "General")
    step = profile.get("step", 1)
    difficulty = profile.get("difficulty", "easy")

    # The agent expects a message list
    messages = state["messages"]

    # Call the agent
    result = agent.invoke({
        "messages": messages,
        "topic": topic,
        "concept": concept,
        "step": step,
        "difficulty": difficulty
    })

    # The result is an AIMessage (or similar)
    text = result.content if hasattr(result, "content") else str(result)

    # Optionally update profile as before (simple logic)
    profile["current_topic"] = topic
    profile["current_concept"] = concept
    profile["step"] = step + 1

    return {
        "messages": [AIMessage(content=text)],
        "profile": profile,
        "output_response": text
    }