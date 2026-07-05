"""Hybrid retrieval: BM25 + FAISS vector search fused via Reciprocal Rank Fusion."""
import logging
from typing import List, Optional

from .bm25 import BM25Retriever
from .embeddings import EmbeddingModel

logger = logging.getLogger(__name__)

_RRF_K = 60  # standard RRF constant


class HybridRetriever:
    """Combines BM25 lexical and dense vector retrieval using RRF fusion.

    Both searches are synchronous (FAISS + BM25 are CPU-bound in-memory ops),
    so no asyncio.gather needed — they run sequentially and finish in < 50ms.
    """

    def __init__(self, embedder: EmbeddingModel, bm25: BM25Retriever):
        self.embedder = embedder
        self.bm25 = bm25

    def retrieve(
        self,
        query: str,
        chunks: List[dict],       # filtered chunk list from AppState
        vector_search_fn,         # AppState.vector_search callable
        top_n: int = 8,
        pdf_ids: Optional[List[str]] = None,
    ) -> List[dict]:
        """Run BM25 + vector search, fuse with RRF, return top-N chunks."""
        if not chunks:
            return []

        # Dense vector search (against full FAISS index, then filter by pdf_id)
        query_vec = self.embedder.embed_one(query)
        vector_results = vector_search_fn(query_vec, k=top_n * 3)

        # Filter vector results to requested pdf_ids
        if pdf_ids:
            id_set = set(pdf_ids)
            vector_results = [c for c in vector_results if c.get("pdf_id") in id_set]

        # BM25 search (already scoped to filtered chunks)
        bm25_results = self.bm25.retrieve(query, chunks, k=top_n * 3)

        fused = self._rrf(bm25_results, vector_results)
        logger.debug(
            "Hybrid: bm25=%d vector=%d fused=%d returning top-%d",
            len(bm25_results), len(vector_results), len(fused), top_n,
        )
        return fused[:top_n]

    def _rrf(
        self,
        bm25_results: List,      # List[Tuple[dict, float]]
        vector_results: List,    # List[dict]  (with 'vector_score')
    ) -> List[dict]:
        """Merge two ranked lists with Reciprocal Rank Fusion.

        score(doc) = Σ 1 / (k + rank_i)   for each list containing the doc.
        """
        scores: dict[str, float] = {}
        chunks_by_id: dict[str, dict] = {}

        for rank, (chunk, _) in enumerate(bm25_results, start=1):
            cid = chunk["id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (_RRF_K + rank)
            chunks_by_id[cid] = chunk

        for rank, chunk in enumerate(vector_results, start=1):
            cid = chunk["id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (_RRF_K + rank)
            chunks_by_id.setdefault(cid, chunk)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for cid, rrf_score in ranked:
            c = dict(chunks_by_id[cid])
            c["rrf_score"] = round(rrf_score, 6)
            c.pop("_embedding", None)
            result.append(c)
        return result
