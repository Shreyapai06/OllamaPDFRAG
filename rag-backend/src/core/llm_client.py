"""Provider-agnostic LLM client factory.

Both Groq and Ollama expose OpenAI-compatible chat completion endpoints, so a
single openai.AsyncOpenAI instance works for both.  Switch providers by setting
LLM_PROVIDER in the environment — no code changes required.
"""
from openai import AsyncOpenAI

from ..api.config import Settings


def make_llm_client(settings: Settings) -> AsyncOpenAI:
    if settings.LLM_PROVIDER == "ollama":
        return AsyncOpenAI(
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
            api_key="ollama",  # Ollama ignores the key but the field is required
        )
    # default: groq
    return AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=settings.GROQ_API_KEY,
    )


def active_model(settings: Settings) -> str:
    """Return the chat model name for the currently active provider."""
    if settings.LLM_PROVIDER == "ollama":
        return settings.OLLAMA_CHAT_MODEL
    return settings.GROQ_CHAT_MODEL