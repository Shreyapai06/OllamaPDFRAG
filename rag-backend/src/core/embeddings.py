"""Local embeddings via sentence-transformers + FAISS in-memory vector search."""
import logging
from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model(model_name: str) -> SentenceTransformer:
    """Load once, reuse across all requests. First call downloads ~90MB model."""
    logger.info("Loading embedding model: %s", model_name)
    return SentenceTransformer(model_name)


class EmbeddingModel:
    """Wraps sentence-transformers. Produces L2-normalised vectors for cosine similarity."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = _load_model(model_name)
        self.dim: int = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> np.ndarray:
        """Embed a batch of texts. Returns float32 array shape (N, dim), normalised."""
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,   # L2-norm → IndexFlatIP == cosine similarity
            show_progress_bar=False,
            batch_size=32,
        )
        return vectors.astype(np.float32)

    def embed_one(self, text: str) -> np.ndarray:
        """Embed a single string. Returns 1-D float32 array of shape (dim,)."""
        return self.embed([text])[0]
