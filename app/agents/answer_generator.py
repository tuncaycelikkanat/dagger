from app.schemas.query import RetrievedChunk


def generate_mock_answer(
    *,
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str:
    if not retrieved_chunks:
        return (
            "I could not find enough relevant information in the processed document "
            "to answer this question."
        )

    best_chunk = retrieved_chunks[0]

    return (
        f"Based on the retrieved document context, the most relevant information for "
        f"the question '{question}' appears on page {best_chunk.page_number}. "
        f"The document describes DAGGER as a document intelligence system focused on "
        f"document analysis, graphical generation, expert retrieval, and reliable "
        f"source-linked reasoning."
    )