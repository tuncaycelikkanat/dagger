from fastapi import APIRouter, HTTPException, status

from app.retrieval.document_store import load_document_chunks, load_document_metadata
from app.retrieval.keyword_retriever import retrieve_relevant_chunks
from app.schemas.query import DocumentQueryRequest, DocumentQueryResponse

router = APIRouter(prefix="/documents", tags=["Queries"])


@router.post("/{document_id}/query", response_model=DocumentQueryResponse)
def query_document(
    document_id: str,
    request: DocumentQueryRequest,
) -> DocumentQueryResponse:
    try:
        load_document_metadata(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        ) from exc

    try:
        chunks = load_document_chunks(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document has not been processed yet: {document_id}",
        ) from exc

    retrieved_chunks = retrieve_relevant_chunks(
        question=request.question,
        chunks=chunks,
        top_k=request.top_k,
    )

    return DocumentQueryResponse(
        document_id=document_id,
        question=request.question,
        retrieved_chunks=retrieved_chunks,
        status="retrieved",
    )
