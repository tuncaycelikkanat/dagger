import json
from pathlib import Path

from app.core.config import get_settings
from app.schemas.document import DocumentChunk, DocumentMetadata
from app.schemas.embedding import ChunkEmbedding


def save_document_metadata(metadata: DocumentMetadata) -> Path:
    settings = get_settings()
    metadata_dir = Path(settings.metadata_dir)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = metadata_dir / f"{metadata.document_id}.json"
    metadata_path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")

    return metadata_path


def load_document_metadata(document_id: str) -> DocumentMetadata:
    settings = get_settings()
    metadata_path = Path(settings.metadata_dir) / f"{document_id}.json"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata for document_id {document_id} not found.")

    raw_data = json.loads(metadata_path.read_text(encoding="utf-8"))
    return DocumentMetadata.model_validate(raw_data)


def save_document_chunks(document_id: str, chunks: list[DocumentChunk]) -> Path:
    settings = get_settings()

    processed_dir = Path(settings.processed_dir) / document_id
    processed_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = processed_dir / "chunks.json"
    chunks_data = [chunk.model_dump() for chunk in chunks]
    chunks_path.write_text(json.dumps(chunks_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return chunks_path

def load_document_chunks(document_id: str) -> list[DocumentChunk]:
    settings = get_settings()
    chunks_path = Path(settings.processed_dir) / document_id / "chunks.json"

    if not chunks_path.exists():
        raise FileNotFoundError(f"Chunks for document_id {document_id} not found.")

    raw_data = json.loads(chunks_path.read_text(encoding="utf-8"))
    return [DocumentChunk.model_validate(chunk) for chunk in raw_data]

def save_chunk_embeddings(document_id: str, embeddings: list[ChunkEmbedding]) -> Path:
    settings = get_settings()

    processed_dir = Path(settings.processed_dir) / document_id
    processed_dir.mkdir(parents=True, exist_ok=True)

    embeddings_path = processed_dir / "embeddings.json"
    embeddings_data = [embedding.model_dump() for embedding in embeddings]
    embeddings_path.write_text(
        json.dumps(embeddings_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return embeddings_path

def load_chunk_embeddings(document_id: str) -> list[ChunkEmbedding]:
    settings = get_settings()
    embeddings_path = Path(settings.processed_dir) / document_id / "embeddings.json"

    if not embeddings_path.exists():
        raise FileNotFoundError(f"Embeddings for document_id {document_id} not found.")

    raw_data = json.loads(embeddings_path.read_text(encoding="utf-8"))
    return [ChunkEmbedding.model_validate(embedding) for embedding in raw_data]