from app.retrieval.query_booster import calculate_query_boost


def test_query_boost_prioritizes_numbered_record() -> None:
    question = "15 numaralı dairenin su tüketimini karşılaştır"

    matching_chunk = (
        "14 DA*** 14 2,23 m³ 387,94 TL "
        "15 DA*** 15 1,58 m³ 63,20 TL 310,89 TL "
        "16 DA*** 16 0,00 m³ 123,58 TL"
    )
    unrelated_chunk = (
        "TOPLAM 58 DAİRE 119,79 m³ 20.513,60 TL "
        "Genel açıklama ve bilgilendirme."
    )

    matching_boost = calculate_query_boost(question, matching_chunk)
    unrelated_boost = calculate_query_boost(question, unrelated_chunk)

    assert matching_boost > unrelated_boost
    assert matching_boost >= 0.35
