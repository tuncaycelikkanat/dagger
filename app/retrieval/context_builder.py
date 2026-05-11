from app.schemas.query import RetrievedChunk


def build_context_from_chunks(chunks: list[RetrievedChunk]) -> str:
    context_parts: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[Source {index} | page={chunk.page_number} | chunk_id={chunk.chunk_id}]\n"
            f"{chunk.text}"
        )

    return "\n\n".join(context_parts)