"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 9, 2026

Description:
Integration tests for the FastAPI backend and Gemini
evaluation service using simulated Gemini responses.

Modification History:
November 9, 2026 - Karen Miller
Created the original Gemini integration test.

November 13, 2026 - Karen Miller
Added PDF-to-Gemini integration testing using synthetic
PDF resume data and simulated Gemini responses.
"""

from io import BytesIO

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from backend.app.main import app
from backend.app.services.gemini_service import (
    ComparisonReport,
    SkillFinding,
)
from backend.app.services.pdf_service import extract_pdf_text


client = TestClient(app)


# ============================================================
# TEST 1: Verify Gemini findings reach the API response
# ============================================================

def test_compare_returns_gemini_findings(monkeypatch):
    """
    Verify that the FastAPI endpoint returns findings
    from the Gemini service instead of placeholder data.
    """

    def fake_compare(request):
        return ComparisonReport(
            findings=[
                SkillFinding(
                    skill="SQL",
                    status="documented",
                    evidence="Developed SQL databases."
                )
            ]
        )

    monkeypatch.setattr(
        "backend.app.services.gemini_service.compare_with_gemini",
        fake_compare
    )

    payload = {
        "job_description": "Seeking a developer with SQL database experience.",
        "resume_text": "Developed SQL databases.",
        "required_skills": ["SQL"]
    }

    response = client.post("/api/v1/compare", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["findings"][0]["skill"] == "SQL"
    assert data["findings"][0]["matched"] is True
    assert data["findings"][0]["evidence_citation"] == (
        "Developed SQL databases."
    )
    assert data["requires_human_review"] is True


# ============================================================
# TEST 2: Verify extracted PDF text reaches Gemini
# ============================================================

def test_pdf_resume_reaches_gemini(monkeypatch):
    """
    Extract text from a synthetic PDF resume and
    verify that the existing FastAPI endpoint passes
    that text to the Gemini comparison service.

    Gemini is simulated, so no API key is required.
    """

    # Create a synthetic PDF resume with actual text.
    output = BytesIO()

    pdf = canvas.Canvas(output, pagesize=(612, 792))
    pdf.drawString(50, 700, "Alex Morgan - Synthetic Resume")
    pdf.drawString(
        50, 670,
        "Experience: Developed Python scripts for log analysis."
    )
    pdf.drawString(50, 640, "Skills: Python and SQL")
    pdf.save()

    # Extract the resume text using our PDF service.
    resume_text = extract_pdf_text(output.getvalue())

    assert "Python" in resume_text
    assert "SQL" in resume_text

    # Track whether Gemini receives the extracted text.
    received_requests = []

    def fake_compare(request):
        received_requests.append(request)

        assert "Developed Python scripts" in request.resume
        assert request.required_skills == ["Python"]

        return ComparisonReport(
            findings=[
                SkillFinding(
                    skill="Python",
                    status="documented",
                    evidence=(
                        "Developed Python scripts for log analysis."
                    )
                )
            ]
        )

    # Replace the live Gemini call with our simulated result.
    monkeypatch.setattr(
        "backend.app.services.gemini_service.compare_with_gemini",
        fake_compare
    )

    # Submit the extracted PDF text to the existing endpoint.
    payload = {
        "job_description": (
            "Seeking a developer with Python experience."
        ),
        "resume_text": resume_text,
        "required_skills": ["Python"]
    }

    response = client.post("/api/v1/compare", json=payload)

    # Confirm that FastAPI accepted the extracted PDF text.
    assert response.status_code == 200

    # Confirm the Gemini service received the request.
    assert len(received_requests) == 1

    # Confirm the correct findings were returned.
    data = response.json()

    assert data["candidate_status"] == "evaluated"
    assert data["findings"][0]["skill"] == "Python"
    assert data["findings"][0]["matched"] is True
    assert data["findings"][0]["evidence_citation"] == (
        "Developed Python scripts for log analysis."
    )
    assert data["requires_human_review"] is True
