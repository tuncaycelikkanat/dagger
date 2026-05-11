import re

from app.schemas.document import DocumentChunk
from app.schemas.query import RetrievedChunk


def tokenize(text: str) -> set[str]:
    normalized = text.lower()
    tokens = re.findall(r'\b\w+\b', normalized)
    return {token for token in tokens if len(token) > 2}

def calculate_keyword_score(question_tokens: set[str], chunk_text: str) -> float:
    chunk_tokens = tokenize(chunk_text)
    if not chunk_tokens or not question_tokens:
        return 0.0
    overlap = question_tokens.intersection(chunk_tokens)
    return len(overlap) / len(chunk_tokens)

def retrieve_relevant_chunks(
        *,
    question: str,
        chunks: list[DocumentChunk],
    top_k: int
) -> list[RetrievedChunk]:
    question_tokens = tokenize(question)
    scored_chunks: list[RetrievedChunk] = []

    for chunk in chunks:
        score = calculate_keyword_score(question_tokens,chunk.text)
        if score <= 0:
            continue
        scored_chunks.append(RetrievedChunk(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            char_count=chunk.char_count,
            score=score
        ))
    scored_chunks.sort(key=lambda c: c.score, reverse=True)
    return scored_chunks[:top_k]