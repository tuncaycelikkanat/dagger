from app.schemas.document import DocumentChunk, DocumentPage


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def chunk_pages(
    *,
    document_id: str,
    pages: list[DocumentPage],
    chunk_size: int,
    chunk_overlap: int,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    chunks: list[DocumentChunk] = []

    for page in pages:
        text = normalize_text(page.text)

        if not text:
            continue

        step = chunk_size - chunk_overlap
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = f"{document_id}_p{page.page_number}_c{chunk_index}"

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        text=chunk_text,
                        char_count=len(chunk_text),
                    )
                )

            if end >= len(text):
                break

            start += step
            chunk_index += 1

    return chunks
