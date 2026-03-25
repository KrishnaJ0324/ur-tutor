from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from models.schema import EvaluationResponse
from core.llm import llm_strict
from core.state import GraphState

def eval_node(state: GraphState) -> dict:
    profile = state["profile"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI tutor evaluating a student's answer(s). Return the evaluation strictly matching the output schema.

CRITICAL INSTRUCTIONS:
1. If the 'Expected Answer' contains a 'QUIZ_KEY' with multiple questions:
   - Grade each question individually as strictly RIGHT or WRONG.
   - Calculate the `accuracy` score as a strict mathematical decimal fraction of correct answers (e.g., 2 out of 3 correct = 0.67. 3 out of 3 = 1.0. 1 out of 2 = 0.5).
   - In your `feedback` field, you MUST explain WHY they were right or wrong for EVERY single question. Provide the logical reason the correct option is the best one.
   - Set `is_correct` to true ONLY if they got all questions right, or a strong passing grade (e.g., >= 0.70).

2. If it is a standard single question (not a quiz):
   - Evaluate their understanding conceptually. `accuracy` should be a float from 0.0 to 1.0.
   - Provide standard, encouraging feedback explaining the concept."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "Expected Answer/Key:\n{expected_answer}\n\nEvaluate my answer.")
    ])
    
    chain = prompt | llm_strict.with_structured_output(EvaluationResponse)
    
    expected_answer = profile.get("last_question", "")
    is_quiz = expected_answer.startswith("QUIZ_KEY:")
    
    eval_res = chain.invoke({
        "messages": state["messages"],
        "expected_answer": expected_answer 
    })
    
    score = eval_res.rubric.accuracy
    
    if is_quiz:
        text = f"**Feedback:**\n{eval_res.feedback}\n\n*Score:* {round(score*100)}%\n"
        text += "\nQuiz complete! What new topic should we tackle next?"
        profile["last_question"] = "" 
        profile["active_quiz"] = None  
    else:
        # Standard conversational feedback
        text = eval_res.feedback
        if eval_res.is_correct:
            text += "\n\n*Type 'continue' to keep going, or ask a question if you are curious!*"
        else:
            text += "\n\n*Let's try breaking that down again. Ask for clarification if you're stuck.*"
        profile["last_question"] = ""
        
    return {
        "messages": [AIMessage(content=text)],
        "profile": profile,
        "output_response": text
    }