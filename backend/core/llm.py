"""
core/llm.py
-----------
The single, shared chat model: Anthropic Claude Haiku 4.5 via langchain-anthropic.

Notes:
- Haiku 4.5 does NOT support the `effort` parameter (it errors), so we don't set it.
- We pass a ChatAnthropic *instance* (not a "provider:model" string) so we control
  max_tokens and streaming, and so deepagents can apply Anthropic prompt caching to the
  frozen system prompt + skills catalog.
"""
from langchain_anthropic import ChatAnthropic

from config import settings


def build_model() -> ChatAnthropic:
    return ChatAnthropic(
        model=settings.MODEL_NAME,            # "claude-haiku-4-5"
        max_tokens=settings.MODEL_MAX_TOKENS,
        timeout=120,
        api_key=settings.ANTHROPIC_API_KEY or None,
    )
