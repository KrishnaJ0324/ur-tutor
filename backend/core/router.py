from core.state import GraphState

def router_node(state: GraphState) -> dict:
    message = state["messages"][-1].content.lower()
    profile = state.get("profile", {})
    
    if any(word in message for word in ["quiz", "test me", "test"]):
        return {"next_action": "quiz"}
        
    last_q = profile.get("last_question", "")
    
    if last_q == "difficulty_check":
        return {"next_action": "teach"}
    elif last_q != "" and last_q != "topic_complete":
        return {"next_action": "eval"}
    else:
        return {"next_action": "teach"}

def route_edges(state: GraphState) -> str:
    return state["next_action"]
