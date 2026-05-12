from app.providers.base import LLMProvider
from app.providers.model_roles import ModelRole


class MockProvider(LLMProvider):
    def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        role: ModelRole = ModelRole.DEFAULT,
    ) -> str:
        del system_prompt, temperature

        if not prompt.strip():
            return "No prompt was provided."

        return (
            f"MockProvider response [{role.value}]: Based on the provided document context, "
            "DAGGER is a deterministic document intelligence system designed to analyze "
            "documents, retrieve relevant evidence, and produce source-linked answers."
        )
