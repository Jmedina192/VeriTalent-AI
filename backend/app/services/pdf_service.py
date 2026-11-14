"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 13, 2026

Description:
Extracts readable text from PDF resumes so the existing
Gemini integration can evaluate applicant qualifications.
"""

from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(pdf_data: bytes) -> str:
    """
    Extract plain text from a PDF resume.

    Args:
        pdf_data: PDF file contents as bytes.

    Returns:
        Extracted resume text.

    Raises:
        ValueError: If the PDF is invalid, encrypted,
        empty, or contains no readable text.
    """
    if not pdf_data or not pdf_data.startswith(b"%PDF-"):
        raise ValueError("Invalid or empty PDF file.")

    try:
        reader = PdfReader(BytesIO(pdf_data))

        if reader.is_encrypted:
            raise ValueError("Encrypted PDF files are not supported.")

        if not reader.pages:
            raise ValueError("PDF contains no pages.")

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
