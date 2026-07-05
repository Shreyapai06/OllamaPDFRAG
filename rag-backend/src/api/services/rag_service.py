"""RAG query orchestration — agent execution + in-memory session persistence."""
import logging
import uuid
from datetime import datetime, timezone
from typing import AsyncIterator, List, Optional

from ...core.agent import ReActAgent, AgentResult
from ..state import AppState, Message

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, state: AppState, agent: ReActAgent):
        self.state = state
        self.agent = agent

    def _history(self, session_id: str) -> List[Message]:
        return self.state.get_history(session_id, last_n=6)

    def _save(self, session_id: str, role: str, content: str,
              sources=None, reasoning_steps=None) -> None:
        self.state.add_message(session_id, Message(
            message_id=str(uuid.uuid4()),
            role=role,
            content=content,
            sources=sources,
            reasoning_steps=reasoning_steps,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))

    async def query(
        self,
        question: str,
        model: str,
        pdf_ids: Optional[List[str]],
        session_id: Optional[str],
    ) -> dict:
        session_id = session_id or str(uuid.uuid4())
        self._save(session_id, "user", question)

        # Override model for this request
        self.agent.model = model

        chunks = self.state.get_chunks_for_pdfs(pdf_ids)
        history = self._history(session_id)

        result: AgentResult = await self.agent.run(
            question=question,
            chunks=chunks,
            vector_search_fn=self.state.vector_search,
            pdf_ids=pdf_ids,
            session_history=history,
        )

        self._save(session_id, "assistant", result.answer,
                   sources=result.sources, reasoning_steps=result.reasoning_steps)

        return {
            "answer": result.answer,
            "sources": result.sources,
            "reasoning_steps": result.reasoning_steps,
            "iterations_used": result.iterations_used,
            "session_id": session_id,
            "metadata": {"model_used": model, "chunks_retrieved": len(result.sources)},
        }

    async def stream_query(
        self,
        question: str,
        model: str,
        pdf_ids: Optional[List[str]],
        session_id: Optional[str],
    ) -> AsyncIterator[dict]:
        session_id = session_id or str(uuid.uuid4())
        self._save(session_id, "user", question)
        self.agent.model = model

        chunks = self.state.get_chunks_for_pdfs(pdf_ids)
        history = self._history(session_id)

        full_answer = ""
        sources = []

        async for event in self.agent.stream(
            question=question,
            chunks=chunks,
            vector_search_fn=self.state.vector_search,
            pdf_ids=pdf_ids,
            session_history=history,
        ):
            if event["type"] == "done":
                full_answer = event.get("answer", "")
                sources = event.get("sources", [])
            yield event

        self._save(session_id, "assistant", full_answer, sources=sources)
        yield {"type": "session", "data": session_id}

    def get_messages(self, session_id: str) -> list:
        return [
            {
                "message_id": m.message_id,
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "reasoning_steps": m.reasoning_steps,
                "timestamp": m.timestamp,
            }
            for m in self.state.get_all_messages(session_id)
        ]
