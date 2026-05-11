from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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

@lru_cache
def get_settings() -> Settings:
    return Settings()
