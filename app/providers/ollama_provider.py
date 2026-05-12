from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import LLMProvider
from app.providers.model_roles import ModelRole


class OllamaProvider(LLMProvider):
    def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        role: ModelRole = ModelRole.DEFAULT,
    ) -> str:
        settings = get_settings()
        model_name = self._get_model_name(role)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        payload: dict[str, Any] = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        try:
            response = httpx.post(
                f"{settings.ollama_base_url}/api/generate",
                json=payload,
                timeout=settings.ollama_timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama request failed for model '{model_name}': {exc}") from exc

        data = response.json()
        generated_text = data.get("response")

        if not isinstance(generated_text, str):
            raise RuntimeError("Ollama response did not contain a valid 'response' field.")

        return generated_text.strip()

    def _get_model_name(self, role: ModelRole) -> str:
        settings = get_settings()

        model_map = {
            ModelRole.DEFAULT: settings.ollama_model_default,
            ModelRole.GRAPH_LIBRARIAN: settings.ollama_model_graph_librarian,
            ModelRole.ARCHITECT: settings.ollama_model_architect,
            ModelRole.VISION: settings.ollama_model_vision,
            ModelRole.SANITIZER: settings.ollama_model_sanitizer,
            ModelRole.CODER: settings.ollama_model_coder,
            ModelRole.CRITIC: settings.ollama_model_critic,
            ModelRole.AUDITOR: settings.ollama_model_auditor,
        }

        return model_map.get(role, settings.ollama_model_default)
