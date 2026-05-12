from typing import Any

import httpx

from app.core.config import get_settings


class OllamaEmbeddingProvider:
    def embed_text(self, text: str) -> list[float]:
        settings = get_settings()

        payload: dict[str, Any] = {
            "model": settings.ollama_embedding_model,
            "prompt": text,
        }

        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json=payload,
                timeout=settings.ollama_timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama embedding request failed: {exc}") from exc

        data = response.json()
        embedding = data.get("embedding")

        if not isinstance(embedding, list):
            raise RuntimeError("Ollama embedding response did not contain an embedding list.")

        return [float(value) for value in embedding]


def get_embedding_provider() -> OllamaEmbeddingProvider:
    return OllamaEmbeddingProvider()
