from abc import ABC, abstractmethod

from app.providers.model_roles import ModelRole


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        role: ModelRole = ModelRole.DEFAULT,
    ) -> str:
        pass
