from app.providers.base import LLMProvider
from app.providers.model_roles import ModelRole
from app.retrieval.context_builder import build_context_from_chunks
from app.schemas.query import RetrievedChunk


def build_answer_prompt(
    *,
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str:
    context = build_context_from_chunks(
        retrieved_chunks,
        question=question,
    )

    return f"""
You are DAGGER, a reliable document intelligence assistant.

Rules:
- Use only the provided sources.
- Answer the user's exact question directly.
- Do not summarize the whole document.
- Do not list unrelated apartments, records, customers, rows, sections, or totals.
- If the question contains a specific number, focus only on records matching that number.
- When comparing documents, extract the relevant values from each source and compare them.
- If a value is not present in the sources, say it is not found.
- Keep the answer concise.
- Cite source numbers in the answer like [Source 1].
- Answer in the same language as the user's question.

Question:
{question}

Sources:
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
        system_prompt="Answer strictly from the provided sources. Do not summarize unrelated content.",
        temperature=0.0,
        role=ModelRole.ARCHITECT,
    )

    return answer
