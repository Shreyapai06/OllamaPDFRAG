"""Pydantic request/response schemas."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PDFUploadResponse(BaseModel):
    pdf_id: str
    name: str
    doc_count: int
    page_count: int
    upload_timestamp: str


class PDFListItem(BaseModel):
    pdf_id: str
    name: str
    doc_count: int
    page_count: int
    upload_timestamp: str


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default="llama-3.3-70b-versatile")
    pdf_ids: Optional[List[str]] = None
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    pdf_name: Optional[str] = None
    pdf_id: Optional[str] = None
    chunk_index: int = 0
    page_number: Optional[int] = None
    rrf_score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    reasoning_steps: List[str]
    iterations_used: int
    session_id: str
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    groq_connected: bool
    total_pdfs: int
    total_chunks: int
