from pathlib import Path

import fitz

from app.schemas.document import DocumentPage


def extract_pdf_pages(file_path: Path) -> list[DocumentPage]:
    pages: list[DocumentPage] = []

    with fitz.open(file_path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            pages.append(
                DocumentPage(
                    page_number=page_index,
                    text=text,
                )
            )

    return pages
