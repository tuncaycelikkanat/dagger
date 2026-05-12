from pydantic import BaseModel, ConfigDict


class ChunkEmbedding(BaseModel):
    model_config = ConfigDict(strict=True)

    chunk_id: str
    document_id: str
    page_number: int
    chunk_index: int
    text: str
    char_count: int
    embedding: list[float]