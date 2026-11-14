
"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 13, 2026

Description:
Extracts readable text from PDF resumes for Gemini evaluation.
Validates PDF structure, readability, file size, and page count.

Modification History:
November 13, 2026 - Karen Miller
Created PDF resume text extraction service.

November 14, 2026 - Karen Miller
Added file-size and page-count restrictions in response
to peer-review feedback on security and performance.
"""

from io import BytesIO

from pypdf import PdfReader


# PDF limits for the Alpha release
MAX_PDF_SIZE = 5 * 1024 * 1024  # 5 MiB
MAX_PDF_PAGES = 4


def extract_pdf_text(pdf_data: bytes) -> str:
    """
    Extract plain text from a PDF resume.

    Args:
        pdf_data: PDF file contents as bytes.

    Returns:
        Extracted resume text.

    Raises:
        ValueError: If the PDF is invalid, encrypted,
        empty, too large, too long, or unreadable.
    """

    # Reject empty files and files without a PDF header.
    if not pdf_data or not pdf_data.startswith(b"%PDF-"):
        raise ValueError("Invalid or empty PDF file.")

    # Reject oversized files before invoking the PDF parser.
    if len(pdf_data) > MAX_PDF_SIZE:
        raise ValueError(
            "PDF exceeds the maximum file size of 5 MB."
        )

    try:
        reader = PdfReader(BytesIO(pdf_data), strict=True)

        if reader.is_encrypted:
            raise ValueError(
                "Encrypted PDF files are not supported."
            )

        if not reader.pages:
            raise ValueError("PDF contains no pages.")

        # Check the page count before extracting any text.
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ValueError(
                "PDF exceeds the maximum limit of 4 pages."
            )

        page_text = [
            page.extract_text() or ""
            for page in reader.pages
        ]

        resume_text = "\n".join(page_text).strip()

        if not resume_text:
            raise ValueError(
                "PDF contains no readable text. "
                "Scanned PDFs may require OCR."
            )

        return resume_text

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            "Unable to read PDF resume."
        ) from exc
