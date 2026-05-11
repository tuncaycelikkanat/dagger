from app.providers.base import LLMProvider


class MockProvider(LLMProvider):
    def generate(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        del system_prompt, temperature

        if not prompt.strip():
            return "No prompt was provided."

        return (
            "MockProvider response: Based on the provided document context, DAGGER is a "
            "deterministic document intelligence system designed to analyze documents, "
            "retrieve relevant evidence, and produce source-linked answers."
        )
