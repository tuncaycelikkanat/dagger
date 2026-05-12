from app.providers.embedding_provider import OllamaEmbeddingProvider
from app.schemas.document import DocumentChunk
from app.schemas.embedding import ChunkEmbedding


def build_chunk_embeddings(
    *,
    chunks: list[DocumentChunk],
    embedding_provider: OllamaEmbeddingProvider,
) -> list[ChunkEmbedding]:
    embeddings: list[ChunkEmbedding] = []

    for chunk in chunks:
        vector = embedding_provider.embed_text(chunk.text)

        embeddings.append(
            ChunkEmbedding(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                char_count=chunk.char_count,
                embedding=vector,
            )
        )

    return embeddings