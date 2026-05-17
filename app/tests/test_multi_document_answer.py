import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_pdf_bytes(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)

    pdf_bytes = bytes(document.tobytes())
    document.close()

    return pdf_bytes


def upload_and_process_pdf(filename: str, text: str) -> str:
    upload_response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                filename,
                create_pdf_bytes(text),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")

    assert process_response.status_code == 200

    return str(document_id)


def test_answer_multiple_documents() -> None:
    first_document_id = upload_and_process_pdf(
        filename="first.pdf",
        text=(
            "Report A. Apartment 15 water usage is 1.58 cubic meters. "
            "Water fee is 63.20 TL. Total amount is 310.89 TL."
        ),
    )
    second_document_id = upload_and_process_pdf(
        filename="second.pdf",
        text=(
            "Report B. Apartment 15 water usage is 2.67 cubic meters. "
            "Water fee is 106.80 TL. Total amount is 948.54 TL."
        ),
    )

    response = client.post(
        "/api/v1/documents/answer",
        json={
            "document_ids": [first_document_id, second_document_id],
            "question": "Compare apartment 15 water usage in both reports.",
            "top_k_per_document": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "answered"
    assert data["document_ids"] == [first_document_id, second_document_id]
    assert data["answer"]
    assert len(data["sources"]) >= 2

    source_document_ids = {source["document_id"] for source in data["sources"]}

    assert first_document_id in source_document_ids
    assert second_document_id in source_document_ids
