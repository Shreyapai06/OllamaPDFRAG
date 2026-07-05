"""Health check — Groq connectivity + in-memory state stats."""
from fastapi import APIRouter
from groq import AsyncGroq
from ..config import settings
from ..dependencies import get_state
from ..models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health():
    state = get_state()

    groq_ok = False
    try:
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        await client.models.list()
        groq_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok" if groq_ok else "degraded",
        groq_connected=groq_ok,
        total_pdfs=len(state.pdfs),
        total_chunks=len(state.chunks),
    )
