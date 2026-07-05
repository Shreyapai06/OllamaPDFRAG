"""ReAct agent — iterative retrieve-then-reason loop powered by Groq."""
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator, List, Optional

from groq import AsyncGroq

from .hybrid import HybridRetriever

logger = logging.getLogger(__name__)

_SUFFICIENCY_PROMPT = """\
You are a RAG assistant. A user asked a question and context was retrieved from PDF documents.

Decide whether the context is sufficient to answer the question accurately.
- If YES: respond with exactly the word ANSWER (nothing else).
- If NO: respond with one refined search query (a single sentence, different angle).

Question: {question}

Context preview:
{preview}

Respond with only 'ANSWER' or a refined query:"""

_SYNTHESIS_PROMPT = """\
Answer the question using ONLY the context below from PDF documents.
Cite the source PDF name for each claim. If context is insufficient, say so clearly.

Context:
{context}

Recent conversation:
{history}

Question: {question}

Answer:"""


@dataclass
class AgentResult:
    answer: str
    sources: List[dict]
    reasoning_steps: List[str]
    iterations_used: int


def _format_context(chunks: List[dict]) -> str:
    parts = []
    for c in chunks:
        src = c.get("pdf_name", "Unknown")
        page = c.get("page_number")
        label = f"[{src}{f', p.{page}' if page else ''}]"
        parts.append(f"{label}\n{c['content']}")
    return "\n\n---\n\n".join(parts)


def _preview(chunks: List[dict], max_chars: int = 500) -> str:
    full = _format_context(chunks)
    return full[:max_chars] + ("…" if len(full) > max_chars else "")


def _format_history(messages: list) -> str:
    if not messages:
        return "(no prior conversation)"
    lines = []
    for m in messages[-6:]:
        role = getattr(m, "role", m.get("role", "?")).capitalize()
        content = getattr(m, "content", m.get("content", ""))[:200]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


class ReActAgent:
    """ReAct loop: retrieve → check sufficiency → re-retrieve or synthesize.

    max_iterations=1 skips the sufficiency check and goes straight to synthesis
    (recommended for Groq free tier to stay within rate limits).
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        groq_api_key: str,
        model: str = "llama-3.3-70b-versatile",
        max_iterations: int = 1,
    ):
        self.retriever = retriever
        self.client = AsyncGroq(api_key=groq_api_key)
        self.model = model
        self.max_iterations = max_iterations

    async def _llm(self, prompt: str, max_tokens: int = 2048) -> str:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()

    async def run(
        self,
        question: str,
        chunks: List[dict],
        vector_search_fn,
        pdf_ids: Optional[List[str]],
        session_history: list,
    ) -> AgentResult:
        steps: List[str] = []
        seen: dict[str, dict] = {}   # dedup by chunk id
        current_query = question

        for iteration in range(1, self.max_iterations + 1):
            steps.append(f"[Iter {iteration}] Retrieving: \"{current_query}\"")

            results = self.retriever.retrieve(
                current_query, chunks, vector_search_fn, top_n=8, pdf_ids=pdf_ids
            )
            new = sum(1 for r in results if r["id"] not in seen)
            for r in results:
                seen.setdefault(r["id"], r)

            steps.append(f"[Iter {iteration}] Got {len(results)} chunks ({new} new), total: {len(seen)}")

            if self.max_iterations == 1:
                steps.append("[Iter 1] Single-iteration mode — synthesizing")
                break

            if iteration == self.max_iterations:
                break

            decision = await self._llm(
                _SUFFICIENCY_PROMPT.format(
                    question=question, preview=_preview(list(seen.values()))
                ),
                max_tokens=100,
            )
            steps.append(f"[Iter {iteration}] Decision: {decision[:80]}")

            if decision.strip().upper() == "ANSWER":
                steps.append(f"[Iter {iteration}] Context sufficient — synthesizing")
                break

            current_query = decision  # refined query for next iteration

        context = _format_context(list(seen.values()))
        history = _format_history(session_history)
        steps.append("Synthesizing answer…")

        answer = await self._llm(
            _SYNTHESIS_PROMPT.format(
                context=context, history=history, question=question
            )
        )

        sources = [
            {
                "pdf_name": c.get("pdf_name"),
                "pdf_id": c.get("pdf_id"),
                "chunk_index": c.get("chunk_index", 0),
                "page_number": c.get("page_number"),
                "rrf_score": c.get("rrf_score"),
            }
            for c in seen.values()
        ]

        return AgentResult(
            answer=answer,
            sources=sources,
            reasoning_steps=steps,
            iterations_used=min(iteration, self.max_iterations),
        )

    async def stream(
        self,
        question: str,
        chunks: List[dict],
        vector_search_fn,
        pdf_ids: Optional[List[str]],
        session_history: list,
    ) -> AsyncIterator[dict]:
        """Yield SSE-compatible event dicts.

        Types: "reasoning" | "token" | "done"
        """
        seen: dict[str, dict] = {}
        current_query = question

        for iteration in range(1, self.max_iterations + 1):
            yield {"type": "reasoning", "data": f"[Iter {iteration}] Retrieving: \"{current_query}\""}

            results = self.retriever.retrieve(
                current_query, chunks, vector_search_fn, top_n=8, pdf_ids=pdf_ids
            )
            for r in results:
                seen.setdefault(r["id"], r)

            yield {"type": "reasoning", "data": f"[Iter {iteration}] {len(results)} chunks retrieved, total: {len(seen)}"}

            if self.max_iterations == 1:
                yield {"type": "reasoning", "data": "Single-iteration mode — synthesizing"}
                break

            if iteration == self.max_iterations:
                break

            decision = await self._llm(
                _SUFFICIENCY_PROMPT.format(
                    question=question, preview=_preview(list(seen.values()))
                ),
                max_tokens=100,
            )
            yield {"type": "reasoning", "data": f"Decision: {decision[:80]}"}

            if decision.strip().upper() == "ANSWER":
                break
            current_query = decision

        yield {"type": "reasoning", "data": "Synthesizing answer…"}

        context = _format_context(list(seen.values()))
        history = _format_history(session_history)
        prompt = _SYNTHESIS_PROMPT.format(
            context=context, history=history, question=question
        )

        full_answer = ""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            full_answer += token
            if token:
                yield {"type": "token", "data": token}

        sources = [
            {
                "pdf_name": c.get("pdf_name"),
                "pdf_id": c.get("pdf_id"),
                "chunk_index": c.get("chunk_index", 0),
                "page_number": c.get("page_number"),
            }
            for c in seen.values()
        ]
        yield {"type": "done", "data": "", "answer": full_answer, "sources": sources}
