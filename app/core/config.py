from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="DAGGER", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    upload_dir: str = Field(default="storage/uploads", alias="UPLOAD_DIR")
    metadata_dir: str = Field(default="storage/metadata", alias="METADATA_DIR")
    processed_dir: str = Field(default="storage/processed", alias="PROCESSED_DIR")

    max_upload_size_mb: int = Field(default=25, alias="MAX_UPLOAD_SIZE_MB")

    chunk_size: int = Field(default=1200, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")

    default_llm_provider: str = Field(default="mock", alias="DEFAULT_LLM_PROVIDER")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_timeout_seconds: int = Field(default=120, alias="OLLAMA_TIMEOUT_SECONDS")

    ollama_model_default: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL_DEFAULT")
    ollama_model_graph_librarian: str = Field(
        default="bge-m3",
        alias="OLLAMA_MODEL_GRAPH_LIBRARIAN",
    )
    ollama_model_architect: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL_ARCHITECT")
    ollama_model_vision: str = Field(default="qwen2.5-vl", alias="OLLAMA_MODEL_VISION")
    ollama_model_sanitizer: str = Field(default="phi3.5", alias="OLLAMA_MODEL_SANITIZER")
    ollama_model_coder: str = Field(default="qwen2.5-coder:7b", alias="OLLAMA_MODEL_CODER")
    ollama_model_critic: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL_CRITIC")
    ollama_model_auditor: str = Field(default="qwen2.5:3b", alias="OLLAMA_MODEL_AUDITOR")

    retrieval_mode: str = Field(default="semantic", alias="RETRIEVAL_MODE")
    embedding_provider: str = Field(default="ollama", alias="EMBEDDING_PROVIDER")
    ollama_embedding_model: str = Field(default="bge-m3:latest", alias="OLLAMA_EMBEDDING_MODEL")

@lru_cache
def get_settings() -> Settings:
    return Settings()
