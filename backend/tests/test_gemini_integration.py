"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 9, 2026

Description:
Integration tests for the FastAPI backend, PDF resume
extraction, Gemini evaluation service, and PII protection
using simulated Gemini responses.

Modification History:
November 9, 2026 - Karen Miller
Created the original Gemini integration test.

November 13, 2026 - Karen Miller
Added PDF-to-Gemini integration testing using synthetic
PDF resume data and simulated Gemini responses.

November 14, 2026 - Karen Miller
Added Gemini PII integration testing to verify that
recognized personal identifiers are removed before
resume text reaches the AI model, while job-related
qualifications and supporting evidence are preserved.
"""

import json
from io import BytesIO
from types import SimpleNamespace

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
        "job_description": (
            "Seeking a developer with SQL database experience."
        ),
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

    # Track whether the comparison service receives the text.
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

    # Replace the comparison service with a simulated result.
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

    # Confirm the comparison service received the request.
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


# ============================================================
# TEST 3: Verify PII is minimized before Gemini request
# ============================================================

def test_gemini_receives_sanitized_resume(monkeypatch):
    """
    Verify that recognized personal identifiers are
    replaced before the Gemini API client receives
    the resume.

    Also verify that the applicant's qualifications
    and exact supporting evidence remain intact.

    Uses a simulated Gemini client.
    No external API call is made.
    """

    # Synthetic applicant information only.
    original_resume = (
        "Name: Alex Morgan\n"
        "Address: 123 Main Street, Richmond, VA\n"
        "Email: alex.morgan@example.com\n"
        "Phone: (555) 234-5678\n"
        "Date of Birth: 01/15/1990\n"
        "SSN: 123-45-6789\n"
        "Skills: Python and SQL\n"
        "Experience: Developed Python scripts for log analysis."
    )

    # Capture the actual prompt passed to the fake Gemini client.
    received_prompts = []

    def fake_generate_content(*, model, contents, config):
        received_prompts.append(contents)

        assert model == "gemini-3.5-flash-lite"

        # Recognized personal identifiers must not appear.
        assert "Alex Morgan" not in contents
        assert "123 Main Street" not in contents
        assert "alex.morgan@example.com" not in contents
        assert "(555) 234-5678" not in contents
        assert "01/15/1990" not in contents
        assert "123-45-6789" not in contents

        # Expected privacy placeholders must appear.
        assert "[NAME REMOVED]" in contents
        assert "[ADDRESS REMOVED]" in contents
        assert "[EMAIL REMOVED]" in contents
        assert "[PHONE REMOVED]" in contents
        assert "[DOB REMOVED]" in contents
        assert "[SSN REMOVED]" in contents

        # Job-related qualifications must be preserved.
        assert "Python and SQL" in contents
        assert (
            "Developed Python scripts for log analysis."
            in contents
        )

        # Return a simulated structured Gemini response.
        simulated_response = {
            "findings": [
                {
                    "skill": "Python",
                    "status": "documented",
                    "evidence": (
                        "Developed Python scripts for log analysis."
                    )
                }
            ]
        }

        return SimpleNamespace(
            text=json.dumps(simulated_response)
        )

    # Construct a fake client with the same method structure
    # used by the real Gemini client.
    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=fake_generate_content
        )
    )

    # Replace only the Gemini client, not the comparison
    # service, so the actual PII minimization code runs.
    monkeypatch.setattr(
        "backend.app.services.gemini_service.get_gemini_client",
        lambda: fake_client
    )

    # Submit the original synthetic resume through FastAPI.
    payload = {
        "job_description": (
            "Seeking a developer with Python experience."
        ),
        "resume_text": original_resume,
        "required_skills": ["Python"]
    }

    response = client.post("/api/v1/compare", json=payload)

    # Confirm successful processing.
    assert response.status_code == 200

    # Confirm Gemini was called exactly once.
    assert len(received_prompts) == 1

    # Confirm the verified evidence appears in the result.
    data = response.json()

    assert data["candidate_status"] == "evaluated"
    assert data["findings"][0]["skill"] == "Python"
    assert data["findings"][0]["matched"] is True
    assert data["findings"][0]["evidence_citation"] == (
        "Developed Python scripts for log analysis."
    )

    # Human review remains required.
    assert data["requires_human_review"] is True
