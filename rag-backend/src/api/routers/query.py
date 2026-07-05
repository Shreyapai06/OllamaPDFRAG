"""Query endpoints: blocking POST and SSE streaming GET."""
import json
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..dependencies import get_rag_service
from ..models import QueryRequest, QueryResponse, SourceInfo
from ..services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest, service: RAGService = Depends(get_rag_service)):
    """Blocking agentic query. Prefer /stream for long answers."""
    try:
        result = await service.query(
            question=request.question,
            model=request.model,
            pdf_ids=request.pdf_ids,
            session_id=request.session_id,
        )
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(500, f"Query failed: {e}")

    return QueryResponse(
        answer=result["answer"],
        sources=[SourceInfo(**s) for s in result["sources"]],
        reasoning_steps=result["reasoning_steps"],
        iterations_used=result["iterations_used"],
        session_id=result["session_id"],
        metadata=result["metadata"],
    )


@router.get("/stream")
async def stream_query(
    question: str = Query(..., min_length=1, max_length=2000),
    model: str = Query(default="llama-3.3-70b-versatile"),
    pdf_ids: Optional[List[str]] = Query(default=None),
    session_id: Optional[str] = Query(default=None),
    service: RAGService = Depends(get_rag_service),
):
    """Server-Sent Events streaming query.

    Events:
      data: {"type": "reasoning", "data": "...step..."}
      data: {"type": "token",     "data": "...token..."}
      data: {"type": "done",      "answer": "...", "sources": [...]}
      data: {"type": "session",   "data": "session-id"}
    """
    async def generate():
        try:
            async for event in service.stream_query(
                question=question, model=model,
                pdf_ids=pdf_ids, session_id=session_id,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str, service: RAGService = Depends(get_rag_service)):
    return service.get_messages(session_id)
