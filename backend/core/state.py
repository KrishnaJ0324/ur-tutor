from typing import TypedDict, Annotated, List, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ProfileState(TypedDict):
    current_topic: str
    current_concept: str
    step: int
    difficulty: str
    last_question: str

class GraphState(TypedDict):
    # 'messages' uses the `add_messages` reducer to automatically append new messages to the list
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Internal user profile memory to manage course progress
    profile: ProfileState
    
    # Internal routing flag set by the intent router node
    next_action: str
    
    # The actual output string to stream to the user
    output_response: str
