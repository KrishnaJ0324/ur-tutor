from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from core.state import GraphState
from core.router import router_node, route_edges
from agents.master import teach_node
from agents.quiz import quiz_node
from agents.evaluation import eval_node

def build_workflow():
    builder = StateGraph(GraphState)
    
    # Add nodes
    builder.add_node("router", router_node)
    builder.add_node("teach", teach_node)
    builder.add_node("quiz", quiz_node)
    builder.add_node("eval", eval_node)
    
    # 1. Always start at the router
    builder.add_edge(START, "router")
    
    # 2. Router directs traffic based on the 'next_action' state variable
    builder.add_conditional_edges(
        "router",
        route_edges,
        {
            "teach": "teach",
            "quiz": "quiz",
            "eval": "eval"
        }
    )
    
    # 3. All distinct agent nodes terminate the graph when done
    builder.add_edge("teach", END)
    builder.add_edge("quiz", END)
    builder.add_edge("eval", END)
    
    # Checkpointer provides the crucial short-term conversational memory
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    return graph

# Export a compiled singleton instance
app_graph = build_workflow()
