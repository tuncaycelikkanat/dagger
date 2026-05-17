import re

from app.retrieval.query_booster import extract_query_numbers, extract_query_terms
from app.schemas.query import RetrievedChunk


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    return text[:max_chars].rstrip() + "\n...[truncated]"


def find_numbered_record_start(text: str, number: str) -> int | None:
    patterns = [
        rf"(?<!\d){re.escape(number)}\s+DA\*+",
        rf"(?<!\d){re.escape(number)}\s+D[A-ZÜĞİŞÖÇ]*",
        rf"daire\s+{re.escape(number)}(?!\d)",
        rf"apartment\s+{re.escape(number)}(?!\d)",
        rf"(?<!\d){re.escape(number)}(?!\d)",
    ]

    normalized_text = text.casefold()

    for pattern in patterns:
        match = re.search(pattern.casefold(), normalized_text)
        if match:
            return match.start()

    return None


def find_next_numbered_record_start(text: str, start: int, current_number: str) -> int | None:
    next_number = str(int(current_number) + 1)

    patterns = [
        rf"(?<!\d){re.escape(next_number)}\s+DA\*+",
        rf"(?<!\d){re.escape(next_number)}\s+D[A-ZÜĞİŞÖÇ]*",
    ]

    normalized_text = text.casefold()
    search_area = normalized_text[start + 1 :]

    positions: list[int] = []

    for pattern in patterns:
        match = re.search(pattern.casefold(), search_area)
        if match:
            positions.append(start + 1 + match.start())

    if not positions:
        return None

    return min(positions)


def extract_numbered_record_snippet(
    *,
    text: str,
    question: str,
    max_chars: int,
) -> str | None:
    numbers = extract_query_numbers(question)

    for number in numbers:
        record_start = find_numbered_record_start(text, number)

        if record_start is None:
            continue

        record_end = find_next_numbered_record_start(
            text=text,
            start=record_start,
            current_number=number,
        )

        if record_end is None:
            record_end = min(record_start + max_chars, len(text))

        snippet = text[record_start:record_end].strip()

        if len(snippet) > max_chars:
            snippet = truncate_text(snippet, max_chars)

        return snippet

    return None


def find_best_anchor_index(text: str, question: str) -> int:
    normalized_text = text.casefold()

    for number in extract_query_numbers(question):
        record_start = find_numbered_record_start(text, number)
        if record_start is not None:
            return record_start

    for term in extract_query_terms(question):
        index = normalized_text.find(term)
        if index >= 0:
            return index

    return 0


def extract_relevant_snippet(
    *,
    text: str,
    question: str,
    max_chars: int,
) -> str:
    numbered_record = extract_numbered_record_snippet(
        text=text,
        question=question,
        max_chars=max_chars,
    )

    if numbered_record:
        return numbered_record

    if len(text) <= max_chars:
        return text

    anchor_index = find_best_anchor_index(text, question)

    half_window = max_chars // 2
    start = max(anchor_index - half_window, 0)
    end = min(start + max_chars, len(text))

    if end - start < max_chars:
        start = max(end - max_chars, 0)

    snippet = text[start:end].strip()

    if start > 0:
        snippet = "[...]\n" + snippet

    if end < len(text):
        snippet = snippet + "\n[...]"

    return snippet


def build_context_from_chunks(
    chunks: list[RetrievedChunk],
    *,
    question: str | None = None,
    max_chars_per_chunk: int = 900,
    max_total_chars: int = 5000,
) -> str:
    context_parts: list[str] = []
    total_chars = 0

    for index, chunk in enumerate(chunks, start=1):
        if question:
            chunk_text = extract_relevant_snippet(
                text=chunk.text,
                question=question,
                max_chars=max_chars_per_chunk,
            )
        else:
            chunk_text = truncate_text(chunk.text, max_chars_per_chunk)

        part = (
            f"[Source {index} | document_id={chunk.document_id} | "
            f"page={chunk.page_number} | chunk_id={chunk.chunk_id}]\n"
            f"{chunk_text}"
        )

        if total_chars + len(part) > max_total_chars:
            break

        context_parts.append(part)
        total_chars += len(part)

    return "\n\n".join(context_parts)
