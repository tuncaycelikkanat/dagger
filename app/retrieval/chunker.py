from app.schemas.document import DocumentChunk, DocumentPage


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line]

    return "\n".join(non_empty_lines)


def split_text_units(text: str) -> list[str]:
    normalized = normalize_text(text)

    if not normalized:
        return []

    units: list[str] = []
    buffer: list[str] = []

    for line in normalized.splitlines():
        clean_line = line.strip()

        if not clean_line:
            continue

        buffer.append(clean_line)

        if clean_line.endswith((".", ":", ";", "?", "!")):
            units.append(" ".join(buffer))
            buffer = []

    if buffer:
        units.append(" ".join(buffer))

    return [unit.strip() for unit in units if unit.strip()]


def split_oversized_unit(
    *,
    text: str,
    max_size: int,
) -> list[str]:
    if len(text) <= max_size:
        return [text]

    parts: list[str] = []
    words = text.split()
    current_words: list[str] = []

    for word in words:
        candidate = " ".join([*current_words, word])

        if len(candidate) > max_size and current_words:
            parts.append(" ".join(current_words))
            current_words = [word]
        else:
            current_words.append(word)

    if current_words:
        parts.append(" ".join(current_words))

    return parts


def create_document_chunk(
    *,
    document_id: str,
    page_number: int,
    chunk_index: int,
    text: str,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=f"{document_id}_p{page_number}_c{chunk_index}",
        document_id=document_id,
        page_number=page_number,
        chunk_index=chunk_index,
        text=text,
        char_count=len(text),
    )


def build_page_chunks(
    *,
    document_id: str,
    page: DocumentPage,
    chunk_size: int,
    chunk_overlap: int,
) -> list[DocumentChunk]:
    units = split_text_units(page.text)

    if not units:
        return []

    chunks: list[DocumentChunk] = []
    current_text = ""
    chunk_index = 0

    for unit in units:
        sub_units = split_oversized_unit(
            text=unit,
            max_size=chunk_size,
        )

        for sub_unit in sub_units:
            candidate = f"{current_text}\n{sub_unit}".strip()

            if len(candidate) <= chunk_size:
                current_text = candidate
                continue

            if current_text:
                chunks.append(
                    create_document_chunk(
                        document_id=document_id,
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        text=current_text,
                    )
                )
                chunk_index += 1

            overlap_text = current_text[-chunk_overlap:].strip() if chunk_overlap > 0 else ""
            current_text = f"{overlap_text}\n{sub_unit}".strip()

    if current_text:
        chunks.append(
            create_document_chunk(
                document_id=document_id,
                page_number=page.page_number,
                chunk_index=chunk_index,
                text=current_text,
            )
        )

    return chunks


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
        page_chunks = build_page_chunks(
            document_id=document_id,
            page=page,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks.extend(page_chunks)

    return chunks
