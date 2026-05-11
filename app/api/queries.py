from fastapi import APIRouter, HTTPException, status

from app.agents.answer_generator import generate_answer
from app.providers.provider_factory import get_llm_provider
from app.retrieval.document_store import load_document_chunks, load_document_metadata
from app.retrieval.keyword_retriever import retrieve_relevant_chunks
from app.schemas.query import (
    DocumentAnswerRequest,
    DocumentAnswerResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    SourceReference,
)

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


@router.post("/{document_id}/answer", response_model=DocumentAnswerResponse)
def answer_document(
    document_id: str,
    request: DocumentAnswerRequest,
) -> DocumentAnswerResponse:
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

    provider = get_llm_provider()

    answer = generate_answer(
        question=request.question,
        retrieved_chunks=retrieved_chunks,
        provider=provider,
    )

    sources = [
        SourceReference(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            score=chunk.score,
        )
        for chunk in retrieved_chunks
    ]

    return DocumentAnswerResponse(
        document_id=document_id,
        question=request.question,
        answer=answer,
        sources=sources,
        status="answered",
    )