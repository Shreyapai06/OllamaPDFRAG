"""PDF management: upload, list, delete."""
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..dependencies import get_pdf_service
from ..models import PDFListItem, PDFUploadResponse
from ..services.pdf_service import PDFService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pdfs", tags=["pdfs"])

_MAX_MB = 50


@router.post("/upload", response_model=PDFUploadResponse, status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    service: PDFService = Depends(get_pdf_service),
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are accepted.")

    # Check size before heavy processing
    data = await file.read()
    if len(data) > _MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {_MAX_MB} MB limit.")

    # Rewind so service.upload_and_process can read again
    from io import BytesIO
    file.file = BytesIO(data)

    try:
        meta = await service.upload_and_process(file)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        logger.exception("PDF processing failed")
        raise HTTPException(500, f"Processing failed: {e}")

    return PDFUploadResponse(
        pdf_id=meta.pdf_id,
        name=meta.name,
        doc_count=meta.doc_count,
        page_count=meta.page_count,
        upload_timestamp=meta.upload_timestamp,
    )


@router.get("", response_model=list[PDFListItem])
def list_pdfs(service: PDFService = Depends(get_pdf_service)):
    return [
        PDFListItem(
            pdf_id=m.pdf_id,
            name=m.name,
            doc_count=m.doc_count,
            page_count=m.page_count,
            upload_timestamp=m.upload_timestamp,
        )
        for m in service.list_pdfs()
    ]


@router.delete("/{pdf_id}", status_code=204)
async def delete_pdf(pdf_id: str, service: PDFService = Depends(get_pdf_service)):
    deleted = await service.delete_pdf(pdf_id)
    if not deleted:
        raise HTTPException(404, "PDF not found.")
