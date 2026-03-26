"""
agents/quiz.py
--------------
This is the specialized Tester AI Agent.
When the traffic cop router detects the user wants to practice, it bypasses conversational AI entirely 
and forces the LLM to output a strict `QuizResponse` JSON block containing exactly 4 randomized multiple-choice 
questions about the topic they just learned.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from models.schema import QuizResponse
from core.llm import llm_strict
from core.state import GraphState

@tool
def fetch_difficulty_guidelines(difficulty: str) -> str:
    """Tool utilized autonomously by the Quiz Sub-Agent to fetch standard academic guidelines dynamically based on learner difficulty."""
    if difficulty.lower() == "advanced":
        return "Guideline: Use highly complex, multi-step scenario questions with dense edge cases."
    elif difficulty.lower() == "intermediate":
        return "Guideline: Test applied logic, formulas, and real-world implementations."
    return "Guideline: Keep vocabulary simple and focus strictly on introductory taxonomy."

def quiz_node(state: GraphState) -> dict:
    profile = state["profile"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Quiz Generator for an AI tutoring system. Your HIGHEST PRIORITY is to generate a quiz on the EXACT topic the user requests in their latest message. 

STRICT RULES:
1. Every single question MUST directly test knowledge of the chosen concept.
2. Each question MUST have exactly 4 options.
3. Generate 2-3 questions at the specified difficulty based strictly on your Tool Guidelines.
4. The answer field must contain the full correct answer text.
5. In your response output, set the `topic` and `concept` fields to exactly what you are quizzing them on."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "Current Course Context: Topic={topic}, Concept={concept}, Difficulty={difficulty}\nTool Guidelines: {tool_obs}")
    ])
    
    chain = prompt | llm_strict.with_structured_output(QuizResponse)
    
    difficulty_pref = profile.get("difficulty", "easy")
    
    # Autonomous Tool decision Phase
    llm_with_tools = llm_strict.bind_tools([fetch_difficulty_guidelines])
    t_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the pre-processing Quiz Agent. Call your specialized tool exactly once to fetch appropriate academic test-writing parameters."),
        ("human", "Difficulty: {diff}")
    ])
    t_chain = t_prompt | llm_with_tools
    
    tool_obs = "Use standard question formulas."
    try:
        t_res = t_chain.invoke({"diff": difficulty_pref})
        if t_res.tool_calls:
             print(f"🛠️ [Tester Sub-Agent] Executing Autonomous Tool Call: {t_res.tool_calls[0]['name']}")
             tool_obs = fetch_difficulty_guidelines.invoke(t_res.tool_calls[0]["args"])
    except Exception as e:
        pass
    
    quiz_res = chain.invoke({
        "messages": state["messages"],
        "topic": profile.get("current_topic", "General"),
        "concept": profile.get("current_concept", "Review"),
        "difficulty": difficulty_pref,
        "tool_obs": tool_obs
    })
    
    profile["current_topic"] = quiz_res.topic
    profile["current_concept"] = quiz_res.concept
    
    text = "Here is your interactive quiz! Please select the best option for each question below:"
    labels = ["A", "B", "C", "D"]
    quiz_key_context = "QUIZ_KEY:\n"
    active_quiz_data = []
    
    for i, q in enumerate(quiz_res.questions, 1):
        options_str = ""
        for j, opt in enumerate(q.options[:4]): 
            opt_line = f"   {labels[j]}) {opt}\n"
            options_str += opt_line
        
        active_quiz_data.append({
            "id": i,
            "question": q.question,
            "options": q.options[:4]
        })
        
        quiz_key_context += f"Q{i}: {q.question}\nOptions:\n{options_str}Correct Answer: {q.answer}\n\n"
    
    profile["last_question"] = quiz_key_context
    profile["active_quiz"] = active_quiz_data
    
    return {
        "messages": [AIMessage(content=text)],
        "profile": profile,
        "output_response": text
    }