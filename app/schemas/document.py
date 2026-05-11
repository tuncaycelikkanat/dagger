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
