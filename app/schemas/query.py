from pydantic import BaseModel, ConfigDict, Field


class DocumentQueryRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    model_config = ConfigDict(strict=True)

    chunk_id: str
    document_id: str
    page_number: int
    chunk_index: int
    text: str
    char_count: int
    score: float


class SourceReference(BaseModel):
    model_config = ConfigDict(strict=True)

    chunk_id: str
    document_id: str
    page_number: int
    chunk_index: int
    score: float


class DocumentQueryResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    document_id: str
    question: str
    retrieved_chunks: list[RetrievedChunk]
    status: str


class DocumentAnswerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class DocumentAnswerResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    document_id: str
    question: str
    answer: str
    sources: list[SourceReference]
    status: str