"""List available Groq chat models."""
from fastapi import APIRouter, HTTPException
from groq import AsyncGroq
from ..config import settings

router = APIRouter(prefix="/models", tags=["models"])

# Groq's current free-tier open-source models
_GROQ_MODELS = [
    {"name": "llama-3.3-70b-versatile",      "note": "Best reasoning"},
    {"name": "llama-3.1-8b-instant",         "note": "Fastest"},
    {"name": "llama-3.2-3b-preview",         "note": "Ultra-light"},
    {"name": "mixtral-8x7b-32768",           "note": "Long context"},
    {"name": "gemma2-9b-it",                 "note": "Google open model"},
    {"name": "deepseek-r1-distill-llama-70b","note": "Chain-of-thought reasoning"},
]


@router.get("")
async def list_models():
    """Return available Groq models. Falls back to static list if API unreachable."""
    try:
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        response = await client.models.list()
        return {"models": [{"name": m.id} for m in response.data]}
    except Exception:
        # Static fallback — always useful even if Groq API is temporarily unavailable
        return {"models": _GROQ_MODELS}
