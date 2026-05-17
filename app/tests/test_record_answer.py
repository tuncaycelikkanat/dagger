from app.agents.record_answer import build_deterministic_record_answer
from app.schemas.query import RetrievedChunk


def test_build_deterministic_record_answer_compares_two_records() -> None:
    question = "15 numaralı dairenin su tüketimini ve toplam tutarını iki raporda karşılaştır"

    chunks = [
        RetrievedChunk(
            chunk_id="doc_a_p1_c4",
            document_id="doc_a",
            page_number=1,
            chunk_index=4,
            text=(
                "15 DA*** 15 180,00 m² | Müş: 1298949 "
                "211,00 kWh 33.149,00 → 33.360,00 380,75 TL "
                "211,00 × 1,80 ₺ 169,73 TL Ortak Alan Payı "
                "2,67 m³ 123,85 → 126,52 233,02 TL "
                "2,67 m³ × 87,27 ₺ 106,80 TL "
                "2,67 m³ × 40,00 ₺ 35,00 TL 23,25 TL "
                "Muaf Daire Payı 169,73 TL 948,54 TL"
            ),
            char_count=100,
            score=0.9,
        ),
        RetrievedChunk(
            chunk_id="doc_b_p1_c3",
            document_id="doc_b",
            page_number=1,
            chunk_index=3,
            text=(
                "15 DA*** 15 180,00 m² | Müş: 1298949 "
                "1,58 m³ 122,27 → 123,85 124,10 TL "
                "1,58 m³ × 78,54 ₺ 63,20 TL "
                "1,58 m³ × 40,00 ₺ 25,00 TL 8,20 TL "
                "Muaf Daire Payı 90,38 TL 310,89 TL"
            ),
            char_count=100,
            score=0.8,
        ),
    ]

    answer = build_deterministic_record_answer(
        question=question,
        retrieved_chunks=chunks,
    )

    assert answer is not None
    assert "2,67 m³" in answer
    assert "1,58 m³" in answer
    assert "106,80 TL" in answer
    assert "63,20 TL" in answer
    assert "948,54 TL" in answer
    assert "310,89 TL" in answer
    assert "1,09 m³" in answer
    assert "43,60 TL" in answer
    assert "637,65 TL" in answer
