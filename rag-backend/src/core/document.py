"""PDF loading, chunking, and BM25 tokenization — no langchain dependency."""
import io
import logging
import re
from dataclasses import dataclass, field
from typing import List

from pypdf import PdfReader

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    page_content: str
    metadata: dict = field(default_factory=dict)


class DocumentProcessor:
    """Loads PDFs from bytes, splits into chunks, tokenizes for BM25."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def get_page_count(self, file_bytes: bytes) -> int:
        return len(PdfReader(io.BytesIO(file_bytes)).pages)

    def load_pdf(self, file_bytes: bytes, filename: str = "document.pdf") -> List[Chunk]:
        """Parse PDF bytes into one Chunk per page. No disk writes."""
        reader = PdfReader(io.BytesIO(file_bytes))
        chunks = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                chunks.append(Chunk(
                    page_content=text,
                    metadata={"page_number": page_num, "source_file": filename},
                ))
        logger.info("Loaded %d pages from '%s'", len(chunks), filename)
        return chunks

    def split_documents(self, documents: List[Chunk]) -> List[Chunk]:
        """Split page-level chunks into smaller overlapping chunks."""
        result = []
        for doc in documents:
            for chunk_text in self._split_text(doc.page_content):
                result.append(Chunk(
                    page_content=chunk_text,
                    metadata=dict(doc.metadata),
                ))
        logger.info("Split into %d chunks", len(result))
        return result

    def _split_text(self, text: str) -> List[str]:
        """Recursive character splitting — mirrors LangChain's splitter logic."""
        separators = ["\n\n", "\n", ". ", " ", ""]
        return self._recursive_split(text, separators)

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        sep = separators[0]
        remaining_seps = separators[1:]

        if sep == "":
            # Character-level fallback
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunks.append(text[start:end])
                start += self.chunk_size - self.chunk_overlap
            return chunks

        parts = text.split(sep)
        chunks: List[str] = []
        current = ""

        for part in parts:
            candidate = (current + sep + part).lstrip(sep) if current else part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                    # Keep overlap from end of current
                    overlap_start = max(0, len(current) - self.chunk_overlap)
                    current = current[overlap_start:] + sep + part
                    current = current.lstrip(sep)
                else:
                    # Part itself is too large — recurse with next separator
                    chunks.extend(self._recursive_split(part, remaining_seps or [""]))
                    current = ""
        if current.strip():
            chunks.append(current)

        return [c for c in chunks if c.strip()]

    def tokenize(self, text: str) -> List[str]:
        """Lowercase + strip punctuation for BM25 indexing."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return [t for t in text.split() if len(t) > 1]
