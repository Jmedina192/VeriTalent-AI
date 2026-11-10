
"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 9, 2026

Description:
Integration tests for the FastAPI backend and Gemini
evaluation service using simulated Gemini responses.
"""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.gemini_service import (
    ComparisonReport,
    SkillFinding,
)

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
