from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal

app = FastAPI(title="VeriTalent AI API", version="0.1.0")

class EvidenceItem(BaseModel):
    skill: str
    matched: bool
    evidence_citation: Optional[str] = None
    uncertainty_flag: bool = False

class ComparisonRequest(BaseModel):
    job_description: str = Field(..., min_length=10, max_length=10000)
    resume_text: str = Field(..., min_length=10, max_length=25000)

    @field_validator("job_description", "resume_text")
    @classmethod
    def strip_and_validate_nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Input must contain at least 10 non-whitespace characters.")
        return cleaned

class ComparisonResponse(BaseModel):
    candidate_status: Literal["evaluated", "mock_scaffold", "error"]
    findings: List[EvidenceItem]
    requires_human_review: bool = True

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "VeriTalent-AI Backend"}

@app.post("/api/v1/compare", response_model=ComparisonResponse)
def compare_resume(payload: ComparisonRequest):
    """
    Sprint 1 contract endpoint. Returns an explicit mock_scaffold status
    until connected to the Gemini evaluation service in PR #2.
    """
    return ComparisonResponse(
        candidate_status="mock_scaffold",
        findings=[
            EvidenceItem(
                skill="Python / FastAPI",
                matched=True,
                evidence_citation="Resume Section: Technical Skills (Scaffold Mock)",
                uncertainty_flag=False
            )
        ],
        requires_human_review=True
    )
