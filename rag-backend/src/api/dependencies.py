"""FastAPI dependency injection — wires singletons into route handlers."""
from functools import lru_cache

from .config import settings
from .state import app_state, AppState
from ..core.bm25 import BM25Retriever
from ..core.embeddings import EmbeddingModel
from ..core.hybrid import HybridRetriever
from ..core.agent import ReActAgent
from ..core.llm_client import make_llm_client, active_model
from .services.pdf_service import PDFService
from .services.rag_service import RAGService


@lru_cache(maxsize=1)
def _embedder() -> EmbeddingModel:
    return EmbeddingModel(settings.EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _retriever() -> HybridRetriever:
    return HybridRetriever(embedder=_embedder(), bm25=BM25Retriever())


@lru_cache(maxsize=1)
def _agent() -> ReActAgent:
    return ReActAgent(
        retriever=_retriever(),
        client=make_llm_client(settings),
        model=active_model(settings),
        max_iterations=settings.MAX_AGENT_ITERATIONS,
    )


def get_state() -> AppState:
    return app_state


def get_pdf_service() -> PDFService:
    return PDFService(state=app_state, embedder=_embedder())


def get_rag_service() -> RAGService:
    return RAGService(state=app_state, agent=_agent())
