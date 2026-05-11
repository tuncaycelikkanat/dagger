from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.retrieval.chunker import chunk_pages
from app.retrieval.document_store import (
    load_document_metadata,
    save_document_chunks,
    save_document_metadata,
)
from app.retrieval.pdf_text_extractor import extract_pdf_pages
from app.schemas.document import (
    DocumentMetadata,
    DocumentProcessingResponse,
    DocumentUploadResponse,
)
from app.security.hashing import calculate_sha256

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: Annotated[UploadFile, File()],
) -> DocumentUploadResponse:
    settings = get_settings()

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for now.",
        )

    content = await file.read()
    size_bytes = len(content)
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if size_bytes > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large. Max size is {settings.max_upload_size_mb} MB.",
        )

    document_id = f"doc_{uuid4().hex}"
    original_filename = file.filename or "uploaded.pdf"
    safe_filename = Path(original_filename).name

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    storage_filename = f"{document_id}_{safe_filename}"
    storage_path = upload_dir / storage_filename

    storage_path.write_bytes(content)

    sha256_hash = calculate_sha256(storage_path)

    metadata = DocumentMetadata(
        document_id=document_id,
        filename=safe_filename,
        content_type=file.content_type or "application/pdf",
        size_bytes=size_bytes,
        sha256_hash=sha256_hash,
        storage_path=str(storage_path),
        status="uploaded",
    )

    save_document_metadata(metadata)

    return DocumentUploadResponse(
        document_id=metadata.document_id,
        filename=metadata.filename,
        content_type=metadata.content_type,
        size_bytes=metadata.size_bytes,
        sha256_hash=metadata.sha256_hash,
        storage_path=metadata.storage_path,
        status=metadata.status,
    )


@router.post("/{document_id}/process", response_model=DocumentProcessingResponse)
def process_document(document_id: str) -> DocumentProcessingResponse:
    settings = get_settings()

    try:
        metadata = load_document_metadata(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        ) from exc

    pdf_path = Path(metadata.storage_path)

    if not pdf_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stored PDF file not found: {document_id}",
        )

    pages = extract_pdf_pages(pdf_path)

    chunks = chunk_pages(
        document_id=document_id,
        pages=pages,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    chunks_path = save_document_chunks(document_id, chunks)

    return DocumentProcessingResponse(
        document_id=document_id,
        pages_extracted=len(pages),
        chunks_created=len(chunks),
        chunks_path=str(chunks_path),
        status="processed",
    )
