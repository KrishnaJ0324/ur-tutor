"""
core/llm.py
-----------
The single, shared chat model: Anthropic Claude Haiku 4.5 served through OpenRouter.

Notes:
- OpenRouter exposes an OpenAI-compatible API (not the native Anthropic Messages API),
  so we use langchain-openai's ChatOpenAI pointed at OpenRouter's base URL rather than
  ChatAnthropic. The model is selected with OpenRouter's slug ("anthropic/claude-haiku-4.5").
- We pass a ChatOpenAI *instance* (not a "provider:model" string) so we control max_tokens,
  streaming, and the OpenRouter endpoint/credentials.
- Trade-off: routing through OpenRouter's OpenAI-compatible surface means deepagents can no
  longer apply Anthropic-native prompt caching to the frozen system prompt + skills catalog.
  Everything else (teaching/quiz/evaluate, tool calls, streaming) works unchanged.
"""
from langchain_openai import ChatOpenAI

from config import settings


def build_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.MODEL_NAME,            # "anthropic/claude-haiku-4.5"
        max_tokens=settings.MODEL_MAX_TOKENS,
        timeout=120,
        api_key=settings.OPENROUTER_API_KEY or None,
        base_url=settings.OPENROUTER_BASE_URL,
        # Optional OpenRouter attribution headers (used for their dashboards/rankings).
        default_headers={
            "HTTP-Referer": settings.FRONTEND_URL.split(",")[0].strip(),
            "X-Title": "UR Tutor",
        },
    )
