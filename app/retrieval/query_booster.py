import re


def normalize_for_match(text: str) -> str:
    return text.casefold()


def extract_query_numbers(question: str) -> list[str]:
    return re.findall(r"\d+", question)


def extract_query_terms(question: str) -> set[str]:
    normalized = normalize_for_match(question)
    tokens = re.findall(r"\b\w+\b", normalized)

    stopwords = {
        "bir",
        "iki",
        "bu",
        "şu",
        "ve",
        "ile",
        "için",
        "the",
        "and",
        "what",
        "which",
        "that",
        "this",
        "from",
        "both",
    }

    return {token for token in tokens if len(token) > 2 and token not in stopwords}


def has_exact_number(text: str, number: str) -> bool:
    return re.search(rf"(?<!\d){re.escape(number)}(?!\d)", text) is not None


def has_numbered_record_marker(text: str, number: str) -> bool:
    patterns = [
        rf"(?<!\d){re.escape(number)}\s+DA",
        rf"DA\*+\s+{re.escape(number)}(?!\d)",
        rf"daire\s+{re.escape(number)}(?!\d)",
        rf"apartment\s+{re.escape(number)}(?!\d)",
        rf"no\s*[:#-]?\s*{re.escape(number)}(?!\d)",
    ]

    normalized = normalize_for_match(text)

    return any(re.search(pattern.casefold(), normalized) for pattern in patterns)


def calculate_query_boost(question: str, chunk_text: str) -> float:
    normalized_chunk = normalize_for_match(chunk_text)
    numbers = extract_query_numbers(question)
    terms = extract_query_terms(question)

    boost = 0.0

    for number in numbers:
        if has_numbered_record_marker(normalized_chunk, number):
            boost += 0.35
        elif has_exact_number(normalized_chunk, number):
            boost += 0.08

    if terms:
        matched_terms = {term for term in terms if term in normalized_chunk}
        boost += min(len(matched_terms) / len(terms), 1.0) * 0.20

    return boost
