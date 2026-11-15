"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Original Backend: Julio Medina
Integration Changes: Karen Miller & Julio Medina
Date: November 14, 2026

Description:
FastAPI backend connected to the PDF extraction and Gemini evaluation services.
Preserves the shared response format and human review.
"""

import base64
import binascii
from typing import List, Optional, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from backend.app.services import gemini_service, pdf_service


app = FastAPI(title="VeriTalent AI API", version="0.1.0")


class EvidenceItem(BaseModel):
    skill: str
    matched: bool
    evidence_citation: Optional[str] = None
    uncertainty_flag: bool = False


class ComparisonRequest(BaseModel):
    job_description: str = Field(..., min_length=10, max_length=10000)
    resume_text: str = Field(..., min_length=10, max_length=25000)
    required_skills: List[str] = Field(..., min_length=1)

    @field_validator("job_description", "resume_text")
    @classmethod
    def strip_and_validate_nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Input must contain at least 10 non-whitespace characters.")
        return cleaned


class PdfComparisonRequest(BaseModel):
    job_description: str = Field(..., min_length=10, max_length=10000)
    pdf_base64: str = Field(..., min_length=1)
    required_skills: List[str] = Field(..., min_length=1)


class ComparisonResponse(BaseModel):
    candidate_status: Literal["evaluated", "mock_scaffold", "error"]
    findings: List[EvidenceItem]
    requires_human_review: bool = True


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "VeriTalent-AI Backend"
    }


@app.post("/api/v1/compare", response_model=ComparisonResponse)
def compare_resume(payload: ComparisonRequest):

    if not payload.resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Resume text cannot be empty"
        )

    if not payload.job_description.strip():
        raise HTTPException(
            status_code=422,
            detail="Job description cannot be empty"
        )

    cleaned_skills = [
        skill.strip() for skill in payload.required_skills
    ]

    if (
        any(not skill for skill in cleaned_skills)
        or len(set(skill.lower() for skill in cleaned_skills))
        != len(cleaned_skills)
    ):
        raise HTTPException(
            status_code=422,
            detail="Required skills must be unique and nonempty"
        )

    gemini_request = gemini_service.ComparisonRequest(
        resume=payload.resume_text,
        job=payload.job_description,
        required_skills=cleaned_skills
    )

    try:
        report = gemini_service.compare_with_gemini(
            gemini_request
        )

    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="AI evaluation returned invalid results"
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI evaluation is temporarily unavailable"
        )

    findings = []

    for item in report.findings:
        findings.append(
            EvidenceItem(
                skill=item.skill,
                matched=(item.status == "documented"),
                evidence_citation=item.evidence,
                uncertainty_flag=True
            )
        )

    return ComparisonResponse(
        candidate_status="evaluated",
        findings=findings,
        requires_human_review=True
    )


@app.post("/api/v1/compare-pdf", response_model=ComparisonResponse)
def compare_pdf_resume(payload: PdfComparisonRequest):
    """
    Extracts readable text from a base64-encoded PDF resume via pdf_service
    and evaluates it against required job skills using Gemini.
    """
    try:
        pdf_bytes = base64.b64decode(payload.pdf_base64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(
            status_code=422,
            detail="Invalid base64-encoded PDF payload."
        )

    try:
        extracted_text = pdf_service.extract_pdf_text(pdf_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    try:
        comparison_payload = ComparisonRequest(
            job_description=payload.job_description,
            resume_text=extracted_text,
            required_skills=payload.required_skills
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    return compare_resume(comparison_payload)
