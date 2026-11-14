"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Author: Karen Miller
Role: Integration Lead
Date: November 14, 2026

Description:
Minimizes personally identifiable information (PII)
in resume text before external Gemini AI evaluation.
Preserves job-related skills and experience.

Modification History:
November 14, 2026 - Karen Miller
Created the PII minimization service to remove common
personal identifiers, including names, addresses, dates
of birth, email addresses, phone numbers, and Social
Security numbers, before Gemini AI evaluation.
"""

import re


def minimize_pii(resume_text: str) -> str:
    """
    Replace recognized personal identifiers with placeholders.

    Supports common contact information and labeled
    personal information fields.

    This is PII minimization, not complete anonymization.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    sanitized = resume_text

    # --------------------------------------------------------
    # Remove labeled applicant names
    # Example: Name: Alex Morgan
    # --------------------------------------------------------
    sanitized = re.sub(
        r"(?im)^(\s*(?:full\s+name|applicant\s+name|name)"
        r"\s*:\s*)[^\r\n]+",
        r"\g<1>[NAME REMOVED]",
        sanitized,
    )

    # --------------------------------------------------------
    # Remove labeled home addresses
    # Example: Address: 123 Main Street, Richmond, VA
    # --------------------------------------------------------
    sanitized = re.sub(
        r"(?im)^(\s*(?:home\s+address|mailing\s+address|"
        r"street\s+address|address)\s*:\s*)[^\r\n]+",
        r"\g<1>[ADDRESS REMOVED]",
        sanitized,
    )

    # --------------------------------------------------------
    # Remove labeled dates of birth
    # Example: Date of Birth: 01/15/1990
    # --------------------------------------------------------
    sanitized = re.sub(
        r"(?im)^(\s*(?:date\s+of\s+birth|birth\s+date|"
        r"dob)\s*:\s*)[^\r\n]+",
        r"\g<1>[DOB REMOVED]",
        sanitized,
    )

    # --------------------------------------------------------
    # Remove email addresses
    # --------------------------------------------------------
    sanitized = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL REMOVED]",
        sanitized,
    )

    # --------------------------------------------------------
    # Remove U.S. phone numbers
    # --------------------------------------------------------
    sanitized = re.sub(
        r"(?<!\w)(?:\+1[-.\s]?)?"
        r"(?:\(\d{3}\)|\d{3})[-.\s]?"
        r"\d{3}[-.\s]?\d{4}(?!\w)",
        "[PHONE REMOVED]",
        sanitized,
    )

    # --------------------------------------------------------
    # Remove SSNs formatted as XXX-XX-XXXX
    # --------------------------------------------------------
    sanitized = re.sub(
        r"\b\d{3}-\d{2}-\d{4}\b",
        "[SSN REMOVED]",
        sanitized,
    )

    return sanitized
