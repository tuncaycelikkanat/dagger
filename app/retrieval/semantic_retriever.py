import math

from app.providers.embedding_provider import OllamaEmbeddingProvider
from app.retrieval.query_booster import calculate_query_boost
from app.schemas.embedding import ChunkEmbedding
from app.schemas.query import RetrievedChunk


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same length.")

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b, strict=True))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def retrieve_semantic_chunks(
    *,
    question: str,
    embeddings: list[ChunkEmbedding],
    embedding_provider: OllamaEmbeddingProvider,
    top_k: int,
) -> list[RetrievedChunk]:
    query_embedding = embedding_provider.embed_text(question)

    scored_chunks: list[RetrievedChunk] = []

    for chunk_embedding in embeddings:
        semantic_score = cosine_similarity(query_embedding, chunk_embedding.embedding)
        query_boost = calculate_query_boost(question, chunk_embedding.text)
        final_score = semantic_score + query_boost

        scored_chunks.append(
            RetrievedChunk(
                chunk_id=chunk_embedding.chunk_id,
                document_id=chunk_embedding.document_id,
                page_number=chunk_embedding.page_number,
                chunk_index=chunk_embedding.chunk_index,
                text=chunk_embedding.text,
                char_count=chunk_embedding.char_count,
                score=final_score,
            )
        )

    scored_chunks.sort(key=lambda item: item.score, reverse=True)

    return scored_chunks[:top_k]
