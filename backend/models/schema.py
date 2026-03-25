from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    state: Optional[Dict[str, Any]] = None

class EvaluationRubric(BaseModel):
    concept_understanding: float
    accuracy: float

class EvaluationResponse(BaseModel):
    is_correct: bool
    confidence: float
    rubric: EvaluationRubric
    feedback: str

class QuizQuestion(BaseModel):
    question: str
    type: str # conceptual | mcq | code
    options: List[str] # Enforces multiple choice options
    answer: str
    difficulty: str

class QuizResponse(BaseModel):
    topic: str
    concept: str
    questions: List[QuizQuestion]

class TeachingResponse(BaseModel):
    topic: str
    concept: str
    detected_difficulty: str
    needs_difficulty: bool
    explanation: str
    example: Optional[str] = None
    analogy: Optional[str] = None
    question: Optional[str] = None
    is_topic_complete: bool # Signals the router to transition to a quiz