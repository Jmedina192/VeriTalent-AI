"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: October 25, 2026

Description:
Automated unit tests for the Gemini integration service
using pytest. Tests input validation, duplicate skills,
invalid response values, missing skill evaluations,
unsupported evidence quotations, and valid comparisons.
Uses mock Gemini responses to test validation without
making external API requests.

Modification History:
November 8, 2026 - Karen Miller
Added test_unexpected_evidence to verify that AI responses
are rejected when a skill is marked "not_documented" but
still includes supporting evidence.

November 8, 2026 - Karen Miller
Updated imports to support the official VeriTalent AI
team repository folder structure.
"""

import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from backend.app.services import gemini_service
from backend.app.services.gemini_service import (
    ComparisonRequest,
    SkillFinding,
    compare_with_gemini,
)


# ============================================================
# MOCK GEMINI RESPONSE HELPER
# ============================================================

def mock_gemini_response(monkeypatch, findings):
    """
    Replace the real Gemini client with a simulated client.

    This allows automated tests to validate AI responses
    without an API key or external Gemini API calls.
    """

    fake_response = SimpleNamespace(
        text=json.dumps({"findings": findings})
    )

    fake_client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: fake_response
        )
    )

    monkeypatch.setattr(
        gemini_service,
        "client",
        fake_client
    )


# ============================================================
# TEST 1: Reject an empty resume
# ============================================================

def test_empty_resume():
    """
    Verify that a resume cannot be empty.
    """

    with pytest.raises(ValidationError):
        ComparisonRequest(
            resume="",
            job="Python developer",
            required_skills=["Python"]
        )


# ============================================================
# TEST 2: Reject an empty required skills list
# ============================================================

def test_empty_skills():
    """
    Verify that at least one required skill is provided.
    """

    with pytest.raises(ValidationError):
        ComparisonRequest(
            resume="Experience developing Python applications.",
            job="Python developer",
            required_skills=[]
        )


# ============================================================
# TEST 3: Reject an invalid skill status
# ============================================================

def test_invalid_status():
    """
    Verify that only documented or not_documented
    are accepted as valid skill statuses.
    """

    with pytest.raises(ValidationError):
        SkillFinding(
            skill="Python",
            status="qualified",
            evidence="Experience with Python."
        )


# ============================================================
# TEST 4: Reject duplicate required skills
# ============================================================

def test_duplicate_skills():
    """
    Verify that duplicate required skills are rejected.
    """

    request = ComparisonRequest(
        resume="Experience with Python.",
        job="Python developer",
        required_skills=["Python", "Python"]
    )

    with pytest.raises(ValueError, match="Duplicate"):
        compare_with_gemini(request)


# ============================================================
# TEST 5: Reject invented evidence
# ============================================================

def test_invented_evidence(monkeypatch):
    """
    Verify that documented evidence must be an exact
    quotation from the applicant's resume.
    """

    request = ComparisonRequest(
        resume="Experience with Python.",
        job="Python and SQL required",
        required_skills=["Python", "SQL"]
    )

    mock_gemini_response(monkeypatch, [
        {
            "skill": "Python",
            "status": "documented",
            "evidence": "Experience with Python."
        },
        {
            "skill": "SQL",
            "status": "documented",
            "evidence": "Developed enterprise SQL databases."
        }
    ])

    with pytest.raises(ValueError, match="Invalid evidence"):
        compare_with_gemini(request)


# ============================================================
# TEST 6: Reject missing skill evaluations
# ============================================================

def test_missing_skill(monkeypatch):
    """
    Verify that Gemini returns findings for every
    required skill.
    """

    request = ComparisonRequest(
        resume="Experience with Python.",
        job="Python and SQL required",
        required_skills=["Python", "SQL"]
    )

    mock_gemini_response(monkeypatch, [
        {
            "skill": "Python",
            "status": "documented",
            "evidence": "Experience with Python."
        }
    ])

    with pytest.raises(ValueError, match="missing or duplicate"):
        compare_with_gemini(request)


# ============================================================
# TEST 7: Accept a valid comparison
# ============================================================

def test_valid_comparison(monkeypatch):
    """
    Verify that correctly structured findings with
    valid supporting evidence are accepted.
    """

    request = ComparisonRequest(
        resume="Experience with Python.",
        job="Python and SQL required",
        required_skills=["Python", "SQL"]
    )

    mock_gemini_response(monkeypatch, [
        {
            "skill": "Python",
            "status": "documented",
            "evidence": "Experience with Python."
        },
        {
            "skill": "SQL",
            "status": "not_documented",
            "evidence": None
        }
    ])

    report = compare_with_gemini(request)

    assert len(report.findings) == 2

    assert report.findings[0].skill == "Python"
    assert report.findings[0].status == "documented"
    assert report.findings[0].evidence == "Experience with Python."

    assert report.findings[1].skill == "SQL"
    assert report.findings[1].status == "not_documented"
    assert report.findings[1].evidence is None


# ============================================================
# TEST 8: Reject evidence for undocumented skills
# ============================================================

def test_unexpected_evidence(monkeypatch):
    """
    Verify that a skill marked not_documented
    cannot contain supporting evidence.
    """

    request = ComparisonRequest(
        resume="Automated reports with Python.",
        job="Python and SQL required",
        required_skills=["Python", "SQL"]
    )

    mock_gemini_response(monkeypatch, [
        {
            "skill": "Python",
            "status": "documented",
            "evidence": "Automated reports with Python."
        },
        {
            "skill": "SQL",
            "status": "not_documented",
            "evidence": "Developed SQL databases."
        }
    ])

    with pytest.raises(ValueError, match="Unexpected evidence"):
        compare_with_gemini(request)
