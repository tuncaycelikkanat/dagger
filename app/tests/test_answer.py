import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_answer_test_pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "DAGGER is a deterministic multi-agent document intelligence system. "
        "It focuses on reliable document analysis and source-linked answers.",
    )

    pdf_bytes = bytes(document.tobytes())
    document.close()

    return pdf_bytes


def upload_and_process_answer_test_pdf() -> str:
    upload_response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "answer-test.pdf",
                create_answer_test_pdf_bytes(),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")

    assert process_response.status_code == 200

    return str(document_id)


def test_answer_processed_document() -> None:
    document_id = upload_and_process_answer_test_pdf()

    response = client.post(
        f"/api/v1/documents/{document_id}/answer",
        json={
            "question": "What is DAGGER?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_id
    assert data["status"] == "answered"
    assert data["answer"]
    assert len(data["sources"]) >= 1
    assert data["sources"][0]["page_number"] == 1