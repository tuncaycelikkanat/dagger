from fastapi import HTTPException, status

from app.core.config import get_settings
from app.providers.embedding_provider import get_embedding_provider
from app.retrieval.document_store import (
    load_chunk_embeddings,
    load_document_chunks,
    load_document_metadata,
)
from app.retrieval.keyword_retriever import retrieve_relevant_chunks
from app.retrieval.semantic_retriever import retrieve_semantic_chunks
from app.schemas.query import RetrievedChunk


def retrieve_chunks_from_document(
    *,
    document_id: str,
    question: str,
    top_k: int,
) -> list[RetrievedChunk]:
    try:
        load_document_metadata(document_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        ) from exc

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


def retrieve_chunks_from_documents(
    *,
    document_ids: list[str],
    question: str,
    top_k_per_document: int,
) -> list[RetrievedChunk]:
    all_chunks: list[RetrievedChunk] = []

    for document_id in document_ids:
        document_chunks = retrieve_chunks_from_document(
            document_id=document_id,
            question=question,
            top_k=top_k_per_document,
        )
        all_chunks.extend(document_chunks)

    all_chunks.sort(key=lambda chunk: chunk.score, reverse=True)

    return all_chunks
