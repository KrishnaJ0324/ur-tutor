"""
agents/master.py
----------------
This is the central Teacher AI Agent. 
It operates strictly via the Socratic method. If the router detects the user hasn't selected a difficulty, 
this agent halts and forces a prompt. Otherwise, it generates comprehensive textbook-style lessons 
and stops when a topic is fully addressed.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from models.schema import TeachingResponse
from core.llm import llm
from core.state import GraphState

@tool
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

def teach_node(state: GraphState) -> dict:
    profile = state["profile"]
    user_message = state["messages"][-1].content
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI tutor. Your HIGHEST PRIORITY is to teach the EXACT topic/concept the user asks for in their message.

TEACHING RULES:
- If the user asks to learn a NEW topic and you do NOT know their difficulty level yet (Difficulty is empty), you MUST set `needs_difficulty` to true and set `explanation` to "Great! Before we dive in, are you a Beginner, Intermediate, or Advanced learner?". Do NOT teach yet.
- If the user provides a difficulty (e.g. "I am a beginner"), set `detected_difficulty` to "beginner", set `needs_difficulty` to false, and START teaching the actual topic.
- Teach comprehensively. Cover the concept in depth before asking any quiz questions.
- Set `is_topic_complete` to false while still teaching. Only set it to true when the full concept has been covered across multiple steps.
- For early steps (steps 1-3), set `question` to null — just teach, don't quiz.
- For later steps (step 4+), you may include a quick comprehension check question.
- The `topic` and `concept` fields MUST match what you are teaching.

TOPIC EXTRACTION (CRITICAL):
- If the user's latest message explicitly mentions a topic, you MUST teach THAT topic."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "Current Context: Topic={topic}, Concept={concept}, Step={step}, Difficulty={difficulty}\nTool Context: {tool_fact}")
    ])
    
    chain = prompt | llm.with_structured_output(TeachingResponse)
    
    concept = profile.get("current_concept", "Basics")
    
    # Execute the LangChain tool natively
    injected_fact = get_pedagogical_fact.invoke({"concept": concept})
    
    res = chain.invoke({
        "messages": state["messages"],
        "topic": profile.get("current_topic", "General"),
        "concept": concept,
        "step": profile.get("step", 1),
        "difficulty": profile.get("difficulty", "easy"),
        "tool_fact": injected_fact
    })
    
    # Update explicit difficulty if detected
    if res.detected_difficulty and res.detected_difficulty.lower() in ["beginner", "intermediate", "advanced"]:
        profile["difficulty"] = res.detected_difficulty.lower()
        profile["needs_difficulty"] = False
        
    if res.needs_difficulty:
        text = res.explanation
        profile["last_question"] = "difficulty_check"
        profile["needs_difficulty"] = True
    else:
        text = f"**{res.concept}**\n\n{res.explanation}\n"
        if res.example:
            text += f"\n*Example:* {res.example}\n"
        if res.analogy:
            text += f"\n*Analogy:* {res.analogy}\n"
        
        if res.is_topic_complete:
            text += "\n---\n\n🎉 **Topic Complete!** Would you like to proceed to a **quiz**, or learn about **something else**?"
            profile["last_question"] = "topic_complete"
        else:
            if res.question:
                text += f"\n---\n\n**Quick Check:** {res.question}"
                profile["last_question"] = res.question
            else:
                text += "\n---\n\n*Type \"continue\" to keep learning.*"
                
    profile["current_topic"] = res.topic
    profile["current_concept"] = res.concept
    profile["step"] = profile.get("step", 1) + 1
    
    return {
        "messages": [AIMessage(content=text)],
        "profile": profile,
        "output_response": text
    }