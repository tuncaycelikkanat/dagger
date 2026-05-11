from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    sha256_hash: str
    storage_path: str
    status: str


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(strict=True)

    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    sha256_hash: str
    storage_path: str
    status: str


class DocumentPage(BaseModel):
    model_config = ConfigDict(strict=True)

    page_number: int
    text: str


class DocumentChunk(BaseModel):
    model_config = ConfigDict(strict=True)

    chunk_id: str
    document_id: str
    page_number: int
    chunk_index: int
    text: str
    char_count: int


class DocumentProcessingResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    document_id: str
    pages_extracted: int
    chunks_created: int
    chunks_path: str
    status: str
