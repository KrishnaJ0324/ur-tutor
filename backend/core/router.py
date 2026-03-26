"""
core/router.py
--------------
This is the "Traffic Cop" of the architecture. It prevents the AI from getting confused.
Before any AI node fires, this function examines the pristine `GraphState`. Based on strict conditions 
(e.g., if the user needs to pick a difficulty, or if the user explicitly asked for a test), it forces 
the graph to take a precise path.
"""
from core.state import GraphState
from pydantic import BaseModel
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from core.llm import llm

class RouteDecision(BaseModel):
    next_node: Literal["teach", "quiz", "eval"]

def router_node(state: GraphState) -> dict:
    message = state["messages"][-1].content.lower()
    profile = state.get("profile", {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Supervisor Agent managing an AI tutoring framework.
Your job is to read the latest message and actively route traffic to the specialized sub-agents:

1. 'teach': The user wants to learn, select difficulty, or continue the lesson.
2. 'quiz': The user explicitly asks for practice questions, a test, or a quiz.
3. 'eval': The user submitted an answer to an active question or an active quiz.

CRITICAL LOGIC OVERRIDES:
- If 'last_question' == 'difficulty_check', route to 'teach' regardless.
- If 'last_question' == 'topic_complete' and they didn't ask for a quiz, route to 'teach'."""),
        ("human", "Message: {message}\nLast Agent Question: {last_q}")
    ])
    
    chain = prompt | llm.with_structured_output(RouteDecision)
    try:
        decision = chain.invoke({
            "message": message,
            "last_q": profile.get("last_question", "")
        })
        node = decision.next_node
        print(f"👔 [Supervisor Agent] Routing to: {node}")
    except Exception:
        node = "teach"  # Fail-safe
        
    return {"next_action": node}

def route_edges(state: GraphState) -> str:
    return state["next_action"]
