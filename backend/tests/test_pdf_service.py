"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 13, 2026

Description:
Automated tests for extracting readable text from PDF resumes.
Tests use synthetic PDF documents and do not call the
Gemini API.

Modification History:
November 13, 2026 - Karen Miller
Created PDF extraction tests.

November 13, 2026 - Karen Miller
Updated the valid PDF test to generate actual page text
using ReportLab rather than a PDF annotation.

November 14, 2026 - Karen Miller
Added three security and performance tests in response
to peer-review feedback from Brian Marquez. The new tests
verify rejection of PDFs exceeding the 5-MB file-size
limit, rejection of PDFs exceeding four pages, and
acceptance of valid four-page PDF documents.
"""

from io import BytesIO

import pytest
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from backend.app.services.pdf_service import extract_pdf_text


# ============================================================
# TEST 1: Verify readable text is extracted from a valid PDF
# ============================================================

def test_valid_pdf_extracts_text():
    """
    Confirm that readable resume information can be
    extracted from a valid PDF document.
    """
    output = BytesIO()

    pdf = canvas.Canvas(output, pagesize=(612, 792))
    pdf.drawString(50, 700, "Alex Morgan - Synthetic Resume")
    pdf.drawString(50, 670, "Skills: Python, SQL, Cybersecurity")
    pdf.drawString(50, 640, "Experience: Developed Python scripts.")
    pdf.drawString(50, 610, "Education: BS Computer Science")
    pdf.save()

    text = extract_pdf_text(output.getvalue())

    assert "Alex Morgan" in text
    assert "Python" in text
    assert "SQL" in text
    assert "Cybersecurity" in text
    assert "Developed Python scripts." in text
    assert "BS Computer Science" in text


# ============================================================
# TEST 2: Reject an empty PDF file
# ============================================================

def test_empty_pdf_file():
    """
    Confirm that an empty file is rejected.
    """
    with pytest.raises(ValueError, match="Invalid or empty"):
        extract_pdf_text(b"")


# ============================================================
# TEST 3: Reject a file that is not a PDF
# ============================================================

def test_invalid_pdf_file():
    """
    Confirm that non-PDF data is rejected.
    """
    with pytest.raises(ValueError, match="Invalid or empty"):
        extract_pdf_text(b"This is not a PDF")


# ============================================================
# TEST 4: Reject a PDF without readable resume text
# ============================================================

def test_blank_pdf_without_readable_text():
    """
    Confirm that a PDF containing a blank page is rejected
    rather than passing empty content to Gemini.
    """
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    output = BytesIO()
    writer.write(output)

    with pytest.raises(ValueError, match="no readable text"):
        extract_pdf_text(output.getvalue())



# ============================================================
# TEST 5: Reject PDFs larger than 5 MB
# ============================================================

def test_pdf_exceeds_file_size_limit():
    """Reject a PDF exceeding the 5-MB limit."""
    oversized_pdf = b"%PDF-1.4\n" + (
        b"X" * (5 * 1024 * 1024)
    )

    with pytest.raises(ValueError, match="maximum file size"):
        extract_pdf_text(oversized_pdf)


# ============================================================
# TEST 6: Reject PDFs containing more than 4 pages
# ============================================================

def test_pdf_exceeds_page_limit():
    """Reject a PDF containing five pages."""
    writer = PdfWriter()

    for _ in range(5):
        writer.add_blank_page(width=612, height=792)

    output = BytesIO()
    writer.write(output)

    with pytest.raises(ValueError, match="maximum limit of 4 pages"):
        extract_pdf_text(output.getvalue())


# ============================================================
# TEST 7: Accept a valid 4-page PDF
# ============================================================

def test_pdf_at_maximum_page_limit():
    """Accept a readable PDF containing exactly four pages."""
    output = BytesIO()

    pdf = canvas.Canvas(output, pagesize=(612, 792))

    for page_number in range(4):
        pdf.drawString(
            50,
            700,
            f"Page {page_number + 1}: Python and SQL experience"
        )
        pdf.showPage()

    pdf.save()

    text = extract_pdf_text(output.getvalue())

    assert "Page 1" in text
    assert "Page 4" in text
    assert "Python" in text
    assert "SQL" in text
