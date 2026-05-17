import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from app.retrieval.context_builder import extract_relevant_snippet
from app.retrieval.query_booster import extract_query_numbers
from app.schemas.query import RetrievedChunk


@dataclass(frozen=True)
class ExtractedRecord:
    source_index: int
    document_id: str
    chunk_id: str
    page_number: int
    record_number: str
    consumption_m3: Decimal | None
    water_fee_tl: Decimal | None
    total_amount_tl: Decimal | None


def parse_tr_decimal(value: str) -> Decimal | None:
    normalized = value.replace(".", "").replace(",", ".")

    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def format_tr_decimal(value: Decimal, suffix: str) -> str:
    quantized = value.quantize(Decimal("0.01"))
    formatted = f"{quantized:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{formatted} {suffix}"


def extract_record_number(question: str) -> str | None:
    numbers = extract_query_numbers(question)

    if not numbers:
        return None

    return numbers[0]


def extract_m3_values(text: str) -> list[Decimal]:
    matches = re.findall(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*m³", text)

    values: list[Decimal] = []

    for match in matches:
        parsed = parse_tr_decimal(match)
        if parsed is not None:
            values.append(parsed)

    return values


def extract_tl_values(text: str) -> list[Decimal]:
    matches = re.findall(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*TL", text)

    values: list[Decimal] = []

    for match in matches:
        parsed = parse_tr_decimal(match)
        if parsed is not None:
            values.append(parsed)

    return values


def extract_m3_unit_prices(text: str) -> list[Decimal]:
    matches = re.findall(r"m³\s*×\s*(\d{1,3}(?:\.\d{3})*,\d{2})\s*₺", text)

    values: list[Decimal] = []

    for match in matches:
        parsed = parse_tr_decimal(match)
        if parsed is not None:
            values.append(parsed)

    return values


def select_water_unit_price(unit_prices: list[Decimal]) -> Decimal | None:
    if not unit_prices:
        return None

    for price in unit_prices:
        if price == Decimal("40.00"):
            return price

    return unit_prices[-1]


def extract_record_from_chunk(
    *,
    source_index: int,
    question: str,
    chunk: RetrievedChunk,
) -> ExtractedRecord | None:
    record_number = extract_record_number(question)

    if record_number is None:
        return None

    snippet = extract_relevant_snippet(
        text=chunk.text,
        question=question,
        max_chars=900,
    )

    if record_number not in snippet:
        return None

    m3_values = extract_m3_values(snippet)
    tl_values = extract_tl_values(snippet)
    unit_prices = extract_m3_unit_prices(snippet)

    consumption_m3 = m3_values[0] if m3_values else None
    water_unit_price = select_water_unit_price(unit_prices)

    water_fee_tl: Decimal | None = None
    if consumption_m3 is not None and water_unit_price is not None:
        water_fee_tl = consumption_m3 * water_unit_price

    total_amount_tl = tl_values[-1] if tl_values else None

    if consumption_m3 is None and water_fee_tl is None and total_amount_tl is None:
        return None

    return ExtractedRecord(
        source_index=source_index,
        document_id=chunk.document_id,
        chunk_id=chunk.chunk_id,
        page_number=chunk.page_number,
        record_number=record_number,
        consumption_m3=consumption_m3,
        water_fee_tl=water_fee_tl,
        total_amount_tl=total_amount_tl,
    )


def deduplicate_records_by_document(records: list[ExtractedRecord]) -> list[ExtractedRecord]:
    seen_document_ids: set[str] = set()
    unique_records: list[ExtractedRecord] = []

    for record in records:
        if record.document_id in seen_document_ids:
            continue

        seen_document_ids.add(record.document_id)
        unique_records.append(record)

    return unique_records


def build_record_comparison_answer(records: list[ExtractedRecord]) -> str:
    first_record = records[0]
    record_number = first_record.record_number

    lines = [
        f"{record_number} numaralı kayıt için kaynaklardan çıkarılan bilgiler şöyledir:",
        "",
    ]

    for record in records:
        parts = [f"- Source {record.source_index}"]

        if record.consumption_m3 is not None:
            parts.append(f"su tüketimi {format_tr_decimal(record.consumption_m3, 'm³')}")

        if record.water_fee_tl is not None:
            parts.append(f"su tüketim tutarı {format_tr_decimal(record.water_fee_tl, 'TL')}")

        if record.total_amount_tl is not None:
            parts.append(f"toplam tutar {format_tr_decimal(record.total_amount_tl, 'TL')}")

        lines.append(", ".join(parts) + f" [Source {record.source_index}].")

    if len(records) >= 2:
        first = records[0]
        second = records[1]

        lines.append("")
        lines.append("Karşılaştırma:")

        if first.consumption_m3 is not None and second.consumption_m3 is not None:
            difference = first.consumption_m3 - second.consumption_m3
            lines.append(
                "- Su tüketimi farkı: "
                f"{format_tr_decimal(abs(difference), 'm³')} "
                f"({'artış' if difference > 0 else 'azalış' if difference < 0 else 'fark yok'})."
            )

        if first.water_fee_tl is not None and second.water_fee_tl is not None:
            difference = first.water_fee_tl - second.water_fee_tl
            lines.append(
                "- Su tüketim tutarı farkı: "
                f"{format_tr_decimal(abs(difference), 'TL')} "
                f"({'artış' if difference > 0 else 'azalış' if difference < 0 else 'fark yok'})."
            )

        if first.total_amount_tl is not None and second.total_amount_tl is not None:
            difference = first.total_amount_tl - second.total_amount_tl
            lines.append(
                "- Toplam tutar farkı: "
                f"{format_tr_decimal(abs(difference), 'TL')} "
                f"({'artış' if difference > 0 else 'azalış' if difference < 0 else 'fark yok'})."
            )

    return "\n".join(lines)


def build_deterministic_record_answer(
    *,
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str | None:
    record_number = extract_record_number(question)

    if record_number is None:
        return None

    extracted_records: list[ExtractedRecord] = []

    for source_index, chunk in enumerate(retrieved_chunks, start=1):
        record = extract_record_from_chunk(
            source_index=source_index,
            question=question,
            chunk=chunk,
        )

        if record is not None:
            extracted_records.append(record)

    unique_records = deduplicate_records_by_document(extracted_records)

    if not unique_records:
        return None

    return build_record_comparison_answer(unique_records)
