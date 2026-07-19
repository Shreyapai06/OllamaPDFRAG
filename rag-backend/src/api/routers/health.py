"""Health check — LLM provider connectivity + in-memory state stats."""
from fastapi import APIRouter
from ..config import settings
from ..dependencies import get_state
from ..models import HealthResponse
from ...core.llm_client import make_llm_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health():
    state = get_state()

    llm_ok = False
    try:
        client = make_llm_client(settings)
        await client.models.list()
        llm_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok" if llm_ok else "degraded",
        groq_connected=llm_ok,  # field kept as-is for frontend compatibility
        total_pdfs=len(state.pdfs),
        total_chunks=len(state.chunks),
    )