from app.core.config import get_settings
from app.providers.base import LLMProvider
from app.providers.mock_provider import MockProvider


def get_llm_provider() -> LLMProvider:
    settings = get_settings()

    if settings.default_llm_provider == "mock":
        return MockProvider()

    raise ValueError(f"Unsupported LLM provider: {settings.default_llm_provider}")
