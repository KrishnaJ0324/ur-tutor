import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
import traceback

def main():
    try:
        from core.workflow import app_graph
        print("Testing LangGraph Workflow Compilation...")

        user_id = "test_user_123"
        config = {"configurable": {"thread_id": user_id}}

        profile_state = {
            "current_topic": "General",
            "current_concept": "Basics",
            "step": 1,
            "difficulty": "easy",
            "last_question": ""
        }

        human_msg = HumanMessage(content="Teach me about Python Loops!")

        print("Invoking graph...")
        final_state = app_graph.invoke(
            {"messages": [human_msg], "profile": profile_state},
            config=config
        )
        with open("err.txt", "w", encoding="utf-8") as f:
            f.write("SUCCESS\n" + final_state["output_response"])
            
    except Exception as e:
        with open("err.txt", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()
