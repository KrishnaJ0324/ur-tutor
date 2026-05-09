"""
api/routes.py
-------------
This file is the "Bridge" connecting your React frontend to the AI backend.
When a user hits the `/chat` endpoint, this file pulls their conversation 'Thread' out of LangGraph memory,
pipes the newest message into the graph, and securely streams the AI's response text back character-by-character 
(along with a hidden JSON `||STATE:...||` tracking mechanism for the UI to update visually).
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio
import logging
from langchain_core.messages import HumanMessage

from models.schema import ChatRequest, ChatResponse
from core.workflow import app_graph
from db import chat_store

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/reset")
async def reset_profile(request: ChatRequest):
    logger.info("reset_profile invoked | user_id=%r", request.user_id)
    chat_store.delete_session(request.user_id)
    logger.info("reset_profile complete | user_id=%r", request.user_id)
    return {"status": "success"}

@router.post("/session/end")
async def end_session(request: ChatRequest):
    logger.info("end_session invoked | user_id=%r", request.user_id)
    chat_store.delete_session(request.user_id)
    logger.info("end_session complete | user_id=%r", request.user_id)
    return {"status": "deleted"}

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    message = request.message

    logger.info("chat_endpoint invoked | user_id=%r message_len=%d", user_id, len(message or ""))

    config = {"configurable": {"thread_id": user_id}}

    # Load Profile from LangGraph Thread State memory instead of SQL DB
    state = app_graph.get_state(config)
    if state and hasattr(state, "values") and "profile" in state.values:
        profile_state = state.values["profile"]
        logger.debug("chat_endpoint loaded existing profile | user_id=%r profile=%r", user_id, profile_state)
    else:
        profile_state = {
            "current_topic": "",
            "current_concept": "",
            "step": 1,
            "difficulty": "",
            "last_question": ""
        }
        logger.debug("chat_endpoint initialized new profile | user_id=%r", user_id)

    human_msg = HumanMessage(content=message)
    response_text = ""
    updated_profile = profile_state

    chat_store.save_message(user_id, "human", message)
    logger.debug("chat_endpoint saved human message | user_id=%r", user_id)

    try:
        final_state = app_graph.invoke(
            {"messages": [human_msg], "profile": profile_state},
            config=config
        )

        response_text = final_state.get("output_response", "Error generating response.")
        updated_profile = final_state.get("profile", profile_state)
        chat_store.save_message(user_id, "assistant", response_text)
        logger.info("chat_endpoint graph invocation complete | user_id=%r response_len=%d", user_id, len(str(response_text)))

    except Exception as e:
        logger.exception("chat_endpoint graph invocation failed | user_id=%r", user_id)
        response_text = f"⚠️ **Backend Error**\n\nI couldn't reach the AI model provider or graph engine. *Error details: {str(e)}*"

    state_dict = {
        "level": updated_profile.get("level", "beginner"),
        "difficulty": updated_profile.get("difficulty", ""),
        "accuracy_trend": updated_profile.get("accuracy_trend", 0.0),
        "active_quiz": updated_profile.get("active_quiz"),
        "needs_difficulty": updated_profile.get("needs_difficulty", False)
    }
    
    logger.debug("chat_endpoint state_dict for stream | user_id=%r state=%r", user_id, state_dict)

    async def string_streamer():
        words = str(response_text).split(" ")
        for i, word in enumerate(words):
            yield word
            if i < len(words) - 1:
                yield " "
            await asyncio.sleep(0.02)

        yield f"||STATE:{json.dumps(state_dict)}||"
        logger.info("chat_endpoint stream complete | user_id=%r words=%d", user_id, len(words))

    return StreamingResponse(string_streamer(), media_type="text/plain")