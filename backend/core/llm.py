"""
core/llm.py
-----------
The shared chat model: Claude Haiku 4.5 on the native Anthropic Messages API.

UR Tutor is bring-your-own-key, so there is no module-level model instance — build_model()
takes the API key the caller pulled off the request and returns a model bound to it.
"""
from langchain_anthropic import ChatAnthropic

from config import settings


def build_model(api_key: str) -> ChatAnthropic:
    return ChatAnthropic(
        model=settings.MODEL_NAME,            # "claude-haiku-4-5"
        max_tokens=settings.MODEL_MAX_TOKENS,
        timeout=120,
        api_key=api_key,
        base_url=settings.ANTHROPIC_BASE_URL,
    )
