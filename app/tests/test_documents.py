from pathlib import Path

import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_sample_pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "DAGGER is a deterministic document intelligence system. "
        "It extracts text from PDF files and splits content into chunks.",
    )

    pdf_bytes = bytes(document.tobytes())
    document.close()

    return pdf_bytes


def test_upload_rejects_non_pdf() -> None:
    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "test.txt",
                b"hello world",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported for now."


def test_upload_accepts_pdf() -> None:
    pdf_content = create_sample_pdf_bytes()

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "test.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size_bytes"] == len(pdf_content)
    assert data["status"] == "uploaded"
    assert len(data["sha256_hash"]) == 64

    storage_path = Path(data["storage_path"])
    assert storage_path.exists()


def test_process_uploaded_pdf() -> None:
    pdf_content = create_sample_pdf_bytes()

    upload_response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "process-test.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 200

    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")

    assert process_response.status_code == 200

    data = process_response.json()

    assert data["document_id"] == document_id
    assert data["pages_extracted"] == 1
    assert data["chunks_created"] >= 1
    assert data["status"] == "processed"

    chunks_path = Path(data["chunks_path"])
    assert chunks_path.exists()
