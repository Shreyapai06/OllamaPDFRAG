"""PDF ingestion pipeline — upload → parse → chunk → embed → store in memory."""
import hashlib
import logging
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile

from ...core.document import DocumentProcessor
from ...core.embeddings import EmbeddingModel
from ..state import AppState, PDFMeta

logger = logging.getLogger(__name__)

_processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)


class PDFService:
    def __init__(self, state: AppState, embedder: EmbeddingModel):
        self.state = state
        self.embedder = embedder

    async def upload_and_process(self, file: UploadFile) -> PDFMeta:
        """Full ingestion pipeline — no disk writes, entirely in memory.

        Steps:
          1. Read bytes
          2. Parse pages with pypdf
          3. Split into chunks (1000 chars / 200 overlap)
          4. Embed all chunks with sentence-transformers
          5. Store vectors + chunks in AppState
          6. Register PDF metadata
        """
        file_bytes = await file.read()
        filename = file.filename or "document.pdf"

        # Stable unique ID
        content_hash = hashlib.sha256(file_bytes).hexdigest()[:10]
        pdf_id = f"{hashlib.md5(filename.encode()).hexdigest()[:6]}_{content_hash}"

        page_count = _processor.get_page_count(file_bytes)
        documents = _processor.load_pdf(file_bytes, filename)
        chunks = _processor.split_documents(documents)

        if not chunks:
            raise ValueError(f"No extractable text found in '{filename}'.")

        # Build chunk dicts with metadata
        chunk_dicts = []
        texts = []
        for idx, chunk in enumerate(chunks):
            chunk_dicts.append({
                "id": str(uuid.uuid4()),
                "pdf_id": pdf_id,
                "pdf_name": filename,
                "chunk_index": idx,
                "content": chunk.page_content,
                "page_number": chunk.metadata.get("page_number"),
                "tokens": _processor.tokenize(chunk.page_content),
            })
            texts.append(chunk.page_content)

        # Embed all chunks in one batch call (fast on CPU for bge-small)
        vectors = self.embedder.embed(texts)

        # Store embedding inside chunk dict for FAISS rebuild on delete
        for chunk_dict, vec in zip(chunk_dicts, vectors):
            chunk_dict["_embedding"] = vec.tolist()

        self.state.add_chunks(chunk_dicts, vectors)

        meta = PDFMeta(
            pdf_id=pdf_id,
            name=filename,
            doc_count=len(chunk_dicts),
            page_count=page_count,
            upload_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.state.register_pdf(meta)
        logger.info("Ingested '%s': %d chunks, %d pages", filename, len(chunk_dicts), page_count)
        return meta

    async def delete_pdf(self, pdf_id: str) -> bool:
        return self.state.delete_pdf(pdf_id)

    def list_pdfs(self):
        return self.state.list_pdfs()

    def get_pdf(self, pdf_id: str):
        return self.state.get_pdf(pdf_id)
