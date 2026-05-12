from app.providers.base import LLMProvider
from app.providers.model_roles import ModelRole
from app.retrieval.context_builder import build_context_from_chunks
from app.schemas.query import RetrievedChunk


def build_answer_prompt(
    *,
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str:
    context = build_context_from_chunks(retrieved_chunks)

    return f"""
You are DAGGER, a reliable document intelligence assistant.

Answer the user's question using only the provided document context.
If the context is insufficient, say that the document does not contain enough information.

Question:
{question}

Document context:
{context}
""".strip()


def generate_answer(
    *,
    question: str,
    retrieved_chunks: list[RetrievedChunk],
    provider: LLMProvider,
) -> str:
    if not retrieved_chunks:
        return (
            "I could not find enough relevant information in the processed document "
            "to answer this question."
        )

    prompt = build_answer_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
    )

    answer = provider.generate(
        prompt=prompt,
        system_prompt="You answer using only the given document context.",
        temperature=0.0,
        role=ModelRole.ARCHITECT,
    )

    return answer
