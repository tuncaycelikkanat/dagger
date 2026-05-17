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


class MultiDocumentAnswerRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    document_ids: list[str] = Field(min_length=1, max_length=10)
    question: str = Field(min_length=1)
    top_k_per_document: int = Field(default=4, ge=1, le=10)


class MultiDocumentAnswerResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    document_ids: list[str]
    question: str
    answer: str
    sources: list[SourceReference]
    status: str
