"""List available chat models for the active LLM provider."""
import httpx
from fastapi import APIRouter
from ..config import settings
from ...core.llm_client import make_llm_client, active_model

router = APIRouter(prefix="/models", tags=["models"])

_GROQ_FALLBACK = [
    {"name": "llama-3.3-70b-versatile",       "note": "Best reasoning"},
    {"name": "llama-3.1-8b-instant",          "note": "Fastest"},
    {"name": "llama-3.2-3b-preview",          "note": "Ultra-light"},
    {"name": "mixtral-8x7b-32768",            "note": "Long context"},
    {"name": "gemma2-9b-it",                  "note": "Google open model"},
    {"name": "deepseek-r1-distill-llama-70b", "note": "Chain-of-thought reasoning"},
]


@router.get("")
async def list_models():
    if settings.LLM_PROVIDER == "ollama":
        # Fetch installed models from Ollama's native /api/tags endpoint
        try:
            async with httpx.AsyncClient() as http:
                r = await http.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
                r.raise_for_status()
                models = [{"name": m["name"]} for m in r.json().get("models", [])]
                return {"models": models or [{"name": settings.OLLAMA_CHAT_MODEL, "note": "Ollama local"}]}
        except Exception:
            return {"models": [{"name": settings.OLLAMA_CHAT_MODEL, "note": "Ollama local"}]}

    # Groq — fetch live list, fall back to static
    try:
        client = make_llm_client(settings)
        response = await client.models.list()
        return {"models": [{"name": m.id} for m in response.data]}
    except Exception:
        return {"models": _GROQ_FALLBACK}