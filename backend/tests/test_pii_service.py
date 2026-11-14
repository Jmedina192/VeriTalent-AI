"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 14, 2026

Description:
Automated tests for PII minimization in resume text.
Verifies that recognized personal identifiers are removed
while job-related qualifications remain intact.

Modification History:
November 14, 2026 - Karen Miller
Created automated PII minimization tests using synthetic
applicant information. No Gemini API calls are made.
"""

import pytest

from backend.app.services.pii_service import minimize_pii


# ============================================================
# TEST 1: Remove labeled applicant name
# ============================================================

def test_removes_applicant_name():
    resume = (
        "Name: Alex Morgan\n"
        "Experience: Developed Python scripts."
    )

    result = minimize_pii(resume)

    assert "Alex Morgan" not in result
    assert "Name: [NAME REMOVED]" in result


# ============================================================
# TEST 2: Remove email address
# ============================================================

def test_removes_email():
    resume = (
        "Email: alex.morgan@example.com\n"
        "Skills: Python and SQL"
    )

    result = minimize_pii(resume)

    assert "alex.morgan@example.com" not in result
    assert "[EMAIL REMOVED]" in result


# ============================================================
# TEST 3: Remove phone number
# ============================================================

def test_removes_phone():
    resume = (
        "Phone: (555) 234-5678\n"
        "Experience: SQL database development"
    )

    result = minimize_pii(resume)

    assert "(555) 234-5678" not in result
    assert "[PHONE REMOVED]" in result


# ============================================================
# TEST 4: Remove home address
# ============================================================

def test_removes_address():
    resume = (
        "Address: 123 Main Street, Richmond, VA\n"
        "Skills: Cybersecurity"
    )

    result = minimize_pii(resume)

    assert "123 Main Street" not in result
    assert "[ADDRESS REMOVED]" in result


# ============================================================
# TEST 5: Remove date of birth
# ============================================================

def test_removes_date_of_birth():
    resume = (
        "Date of Birth: 01/15/1990\n"
        "Education: BS Computer Science"
    )

    result = minimize_pii(resume)

    assert "01/15/1990" not in result
    assert "[DOB REMOVED]" in result


# ============================================================
# TEST 6: Remove Social Security number
# ============================================================

def test_removes_ssn():
    resume = (
        "SSN: 123-45-6789\n"
        "Skills: Python"
    )

    result = minimize_pii(resume)

    assert "123-45-6789" not in result
    assert "[SSN REMOVED]" in result


# ============================================================
# TEST 7: Preserve job-related qualifications
# ============================================================

def test_preserves_qualifications():
    resume = (
        "Name: Alex Morgan\n"
        "Email: alex.morgan@example.com\n"
        "Skills: Python, SQL, Cybersecurity\n"
        "Experience: Developed Python scripts for log analysis."
    )

    result = minimize_pii(resume)

    assert "Alex Morgan" not in result
    assert "alex.morgan@example.com" not in result
    assert "Python" in result
    assert "SQL" in result
    assert "Cybersecurity" in result
    assert "Developed Python scripts for log analysis." in result


# ============================================================
# TEST 8: Reject empty resume text
# ============================================================

def test_rejects_empty_resume():
    with pytest.raises(ValueError, match="cannot be empty"):
        minimize_pii("")


# ============================================================
# TEST 9: Preserve text when no recognized PII exists
# ============================================================

def test_preserves_text_without_pii():
    resume = (
        "Developed Python scripts and managed SQL databases."
    )

    result = minimize_pii(resume)

    assert result == resume
