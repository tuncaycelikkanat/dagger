from fastapi import APIRouter, HTTPException, status

from app.agents.answer_generator import generate_answer
from app.core.config import get_settings
from app.providers.embedding_provider import get_embedding_provider
from app.providers.provider_factory import get_llm_provider
from app.retrieval.document_store import (
    load_chunk_embeddings,
    load_document_chunks,
    load_document_metadata,
)
from app.retrieval.keyword_retriever import retrieve_relevant_chunks
from app.retrieval.multi_document_retriever import retrieve_chunks_from_documents
from app.retrieval.semantic_retriever import retrieve_semantic_chunks
from app.agents.record_answer import build_deterministic_record_answer
from app.schemas.query import (
    DocumentAnswerRequest,
    DocumentAnswerResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    MultiDocumentAnswerRequest,
    MultiDocumentAnswerResponse,
    RetrievedChunk,
    SourceReference,
)

router = APIRouter(prefix="/documents", tags=["Queries"])


def build_sources(chunks: list[RetrievedChunk]) -> list[SourceReference]:
    return [
        SourceReference(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            score=chunk.score,
        )
        for chunk in chunks
    ]


def retrieve_chunks_for_question(
    *,
    document_id: str,
    question: str,
    top_k: int,
) -> list[RetrievedChunk]:
    settings = get_settings()

    if settings.retrieval_mode == "semantic":
        try:
            embeddings = load_chunk_embeddings(document_id)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Document embeddings not found. "
                    f"Re-process document first: {document_id}"
                ),
            ) from exc

        embedding_provider = get_embedding_provider()

        return retrieve_semantic_chunks(
            question=question,
            embeddings=embeddings,
            embedding_provider=embedding_provider,
            top_k=top_k,
        )

    try:
        chunks = load_document_chunks(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document has not been processed yet: {document_id}",
        ) from exc

    return retrieve_relevant_chunks(
        question=question,
        chunks=chunks,
        top_k=top_k,
    )


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

    retrieved_chunks = retrieve_chunks_for_question(
        document_id=document_id,
        question=request.question,
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

    retrieved_chunks = retrieve_chunks_for_question(
        document_id=document_id,
        question=request.question,
        top_k=request.top_k,
    )

    answer = build_deterministic_record_answer(
        question=request.question,
        retrieved_chunks=retrieved_chunks,
    )

    if answer is None:
        provider = get_llm_provider()

        answer = generate_answer(
            question=request.question,
            retrieved_chunks=retrieved_chunks,
            provider=provider,
        )

    return DocumentAnswerResponse(
        document_id=document_id,
        question=request.question,
        answer=answer,
        sources=build_sources(retrieved_chunks),
        status="answered",
    )


@router.post("/answer", response_model=MultiDocumentAnswerResponse)
def answer_multiple_documents(
    request: MultiDocumentAnswerRequest,
) -> MultiDocumentAnswerResponse:
    retrieved_chunks = retrieve_chunks_from_documents(
        document_ids=request.document_ids,
        question=request.question,
        top_k_per_document=request.top_k_per_document,
    )

    answer = build_deterministic_record_answer(
        question=request.question,
        retrieved_chunks=retrieved_chunks,
    )

    if answer is None:
        provider = get_llm_provider()

        answer = generate_answer(
            question=request.question,
            retrieved_chunks=retrieved_chunks,
            provider=provider,
        )

    used_chunks = retrieved_chunks

    if build_deterministic_record_answer(
            question=request.question,
            retrieved_chunks=retrieved_chunks,
    ) is not None:
        used_chunks = retrieved_chunks[: len(request.document_ids)]

    return MultiDocumentAnswerResponse(
        document_ids=request.document_ids,
        question=request.question,
        answer=answer,
        sources=build_sources(used_chunks),
        status="answered",
    )
