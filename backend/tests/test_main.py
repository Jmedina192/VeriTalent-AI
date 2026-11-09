"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Original Backend Tests: Julio Medina
Integration Updates: Karen Miller
Date: November 9, 2026

Description:
Automated tests for the FastAPI backend, including
health checks, Gemini integration response validation,
and invalid input handling.

Modification History:
November 9, 2026 - Karen Miller
Updated the comparison test to use simulated Gemini
results and verify the returned field values.
"""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.gemini_service import (
    ComparisonReport,
    SkillFinding,
)

client = TestClient(app)


# ============================================================
# TEST 1: Health Check
# ============================================================

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ============================================================
# TEST 2: Verify Comparison Response
# ============================================================

def test_compare_resume_valid_schema(monkeypatch):
    """
    Verify that the comparison endpoint returns the
    expected fields using a simulated Gemini result.
    """

    def fake_compare(request):
        return ComparisonReport(
            findings=[
                SkillFinding(
                    skill="Python",
                    status="documented",
                    evidence="skilled in Python"
                ),
                SkillFinding(
                    skill="FastAPI",
                    status="documented",
                    evidence="FastAPI"
                )
            ]
        )

    monkeypatch.setattr(
        "backend.app.services.gemini_service.compare_with_gemini",
        fake_compare
    )

    payload = {
        "job_description": (
            "Seeking a Python backend developer "
            "with FastAPI experience."
        ),
        "resume_text": (
            "Experienced software developer "
            "skilled in Python and FastAPI."
        ),
        "required_skills": ["Python", "FastAPI"]
    }

    response = client.post("/api/v1/compare", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_status"] == "evaluated"
    assert data["requires_human_review"] is True

    assert len(data["findings"]) == 2

    assert data["findings"][0]["skill"] == "Python"
    assert data["findings"][0]["matched"] is True
    assert data["findings"][0]["evidence_citation"] == (
        "skilled in Python"
    )
    assert data["findings"][0]["uncertainty_flag"] is True

    assert data["findings"][1]["skill"] == "FastAPI"
    assert data["findings"][1]["matched"] is True
    assert data["findings"][1]["evidence_citation"] == (
        "FastAPI"
    )
    assert data["findings"][1]["uncertainty_flag"] is True


# ============================================================
# TEST 3: Reject Invalid Input
# ============================================================

def test_compare_resume_rejects_short_input():
    """
    Verify that short resume and job descriptions
    are rejected by the FastAPI endpoint.
    """

    payload = {
        "job_description": "short",
        "resume_text": "short",
        "required_skills": ["Python"]
    }

    response = client.post("/api/v1/compare", json=payload)

    assert response.status_code == 422
