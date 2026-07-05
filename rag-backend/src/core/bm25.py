"""BM25 lexical retrieval — fully in-memory, no database required."""
import re
from typing import List, Tuple

from rank_bm25 import BM25Okapi


def tokenize(text: str) -> List[str]:
    """Lowercase, strip punctuation, split on whitespace. Min token length 2."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]


class BM25Retriever:
    """Builds a BM25Okapi index in-memory from a list of chunks and scores them."""

    def retrieve(
        self,
        query: str,
        chunks: List[dict],
        k: int = 10,
    ) -> List[Tuple[dict, float]]:
        """Score chunks against query using BM25.

        Args:
            query:  User search query.
            chunks: List of chunk dicts, each with a 'tokens' key (List[str]).
            k:      Max results to return.

        Returns:
            Top-k (chunk, score) tuples sorted by descending score,
            filtered to non-zero scores only.
        """
        if not chunks:
            return []

        corpus = [c.get("tokens") or tokenize(c.get("content", "")) for c in chunks]
        index = BM25Okapi(corpus)
        scores = index.get_scores(tokenize(query))

        ranked = sorted(zip(chunks, scores.tolist()), key=lambda x: x[1], reverse=True)
        return [(c, s) for c, s in ranked if s > 0][:k]
