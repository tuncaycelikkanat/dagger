import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_query_test_pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "DAGGER is a deterministic document intelligence system. "
        "It uses chunking and retrieval to answer questions from documents.",
    )

    pdf_bytes = document.tobytes()
    document.close()

    return bytes(pdf_bytes)


def upload_and_process_test_pdf() -> str:
    upload_response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "query-test.pdf",
                create_query_test_pdf_bytes(),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")

    assert process_response.status_code == 200

    return str(document_id)


def test_query_processed_document() -> None:
    document_id = upload_and_process_test_pdf()

    response = client.post(
        f"/api/v1/documents/{document_id}/query",
        json={
            "question": "What is DAGGER document intelligence?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_id
    assert data["status"] == "retrieved"
    assert len(data["retrieved_chunks"]) >= 1
    assert data["retrieved_chunks"][0]["score"] > 0


def test_query_unprocessed_document_returns_error() -> None:
    upload_response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "unprocessed.pdf",
                create_query_test_pdf_bytes(),
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    document_id = upload_response.json()["document_id"]

    response = client.post(
        f"/api/v1/documents/{document_id}/query",
        json={
            "question": "What is this document about?",
            "top_k": 3,
        },
    )

    assert response.status_code == 400

    detail = response.json()["detail"]

    assert (
            "has not been processed yet" in detail
            or "Document embeddings not found" in detail
    )