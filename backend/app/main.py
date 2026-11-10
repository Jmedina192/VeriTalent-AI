"""
Project: VeriTalent AI
Course: CMSC 495 - Computer Science Capstone
Original Backend: Julio Medina
Integration Changes: Karen Miller
Date: November 9, 2026

Description:
FastAPI backend connected to the Gemini evaluation service.
Preserves the shared response format and human review.
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.app.services import gemini_service


app = FastAPI(title="VeriTalent AI API", version="0.1.0")


class EvidenceItem(BaseModel):
    skill: str
    matched: bool
    evidence_citation: Optional[str] = None
    uncertainty_flag: bool = False


class ComparisonRequest(BaseModel):
    job_description: str = Field(..., min_length=10)
    resume_text: str = Field(..., min_length=10)
    required_skills: List[str] = Field(..., min_length=1)


class ComparisonResponse(BaseModel):
    candidate_status: str
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
