from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from models.schema import QuizResponse
from core.llm import llm_strict
from core.state import GraphState

def quiz_node(state: GraphState) -> dict:
    profile = state["profile"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Quiz Generator for an AI tutoring system. Your HIGHEST PRIORITY is to generate a quiz on the EXACT topic the user requests in their latest message. 

STRICT RULES:
1. Every single question MUST directly test knowledge of the chosen concept.
2. Each question MUST have exactly 4 options.
3. Generate 2-3 questions at the specified difficulty.
4. The answer field must contain the full correct answer text, not just a letter.
5. In your response output, set the `topic` and `concept` fields to exactly what you are quizzing them on."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "Current Course Context (Use ONLY if my last message does not specify a topic): Topic={topic}, Concept={concept}, Difficulty={difficulty}\n\nRemember: Generate questions exclusively about the requested concept.")
    ])
    
    chain = prompt | llm_strict.with_structured_output(QuizResponse)
    
    quiz_res = chain.invoke({
        "messages": state["messages"],
        "topic": profile.get("current_topic", "General"),
        "concept": profile.get("current_concept", "Review"),
        "difficulty": profile.get("difficulty", "easy")
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