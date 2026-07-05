"""In-memory application state — single source of truth for all runtime data.

Lives for the lifetime of the FastAPI process. Data is lost on restart.
Thread-safe for reads; writes are protected by Python's GIL for simple ops.
"""
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import faiss
import numpy as np


@dataclass
class PDFMeta:
    pdf_id: str
    name: str
    doc_count: int
    page_count: int
    upload_timestamp: str


@dataclass
class Message:
    message_id: str
    role: str          # "user" | "assistant"
    content: str
    sources: Optional[list] = None
    reasoning_steps: Optional[list] = None
    timestamp: str = ""


class AppState:
    """Central in-memory store for vectors, chunks, PDFs, and chat sessions."""

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        # FAISS index — IndexFlatIP with L2-normalised vectors = cosine similarity
        self.index: faiss.Index = faiss.IndexFlatIP(embedding_dim)
        # Parallel list: chunks[i] corresponds to FAISS internal index i
        self.chunks: List[dict] = []
        # PDF registry
        self.pdfs: Dict[str, PDFMeta] = {}
        # Chat sessions: session_id → list of Message
        self.sessions: Dict[str, List[Message]] = {}

    # ── Vector + chunk management ──────────────────────────────────────────

    def add_chunks(self, chunks: List[dict], vectors: np.ndarray) -> None:
        """Append chunks and their embeddings to the index."""
        if len(chunks) == 0:
            return
        self.index.add(vectors.astype(np.float32))
        self.chunks.extend(chunks)

    def get_chunks_for_pdfs(self, pdf_ids: Optional[List[str]]) -> List[dict]:
        """Return chunks belonging to the given PDFs (None = all)."""
        if not pdf_ids:
            return self.chunks
        id_set = set(pdf_ids)
        return [c for c in self.chunks if c.get("pdf_id") in id_set]

    def delete_pdf(self, pdf_id: str) -> bool:
        """Remove a PDF and all its chunks. Rebuilds the FAISS index."""
        if pdf_id not in self.pdfs:
            return False

        # Filter out deleted chunks
        kept_chunks = [c for c in self.chunks if c.get("pdf_id") != pdf_id]

        # Rebuild FAISS index from kept embeddings
        new_index = faiss.IndexFlatIP(self.embedding_dim)
        if kept_chunks:
            kept_vecs = np.array(
                [c["_embedding"] for c in kept_chunks], dtype=np.float32
            )
            new_index.add(kept_vecs)

        self.index = new_index
        self.chunks = kept_chunks
        del self.pdfs[pdf_id]
        return True

    def vector_search(self, query_vec: np.ndarray, k: int) -> List[dict]:
        """Cosine similarity search. Returns up to k chunks with scores."""
        if self.index.ntotal == 0:
            return []
        k = min(k, self.index.ntotal)
        scores, indices = self.index.search(
            query_vec.reshape(1, -1).astype(np.float32), k
        )
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            chunk = dict(self.chunks[idx])
            chunk["vector_score"] = float(score)
            chunk.pop("_embedding", None)   # don't leak raw vectors
            results.append(chunk)
        return results

    # ── PDF registry ───────────────────────────────────────────────────────

    def register_pdf(self, meta: PDFMeta) -> None:
        self.pdfs[meta.pdf_id] = meta

    def list_pdfs(self) -> List[PDFMeta]:
        return list(self.pdfs.values())

    def get_pdf(self, pdf_id: str) -> Optional[PDFMeta]:
        return self.pdfs.get(pdf_id)

    # ── Chat sessions ──────────────────────────────────────────────────────

    def ensure_session(self, session_id: str) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = []

    def add_message(self, session_id: str, msg: Message) -> None:
        self.ensure_session(session_id)
        self.sessions[session_id].append(msg)

    def get_history(self, session_id: str, last_n: int = 6) -> List[Message]:
        return self.sessions.get(session_id, [])[-last_n:]

    def get_all_messages(self, session_id: str) -> List[Message]:
        return self.sessions.get(session_id, [])


# Module-level singleton — imported by dependencies.py
app_state = AppState()
