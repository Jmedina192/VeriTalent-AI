from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="VeriTalent AI API", version="0.1.0")

class EvidenceItem(BaseModel):
    skill: str
    matched: bool
    evidence_citation: Optional[str] = None
    uncertainty_flag: bool = False

class ComparisonRequest(BaseModel):
    job_description: str = Field(..., min_length=10)
    resume_text: str = Field(..., min_length=10)

class ComparisonResponse(BaseModel):
    candidate_status: str
    findings: List[EvidenceItem]
    requires_human_review: bool = True

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "VeriTalent-AI Backend"}

@app.post("/api/v1/compare", response_model=ComparisonResponse)
def compare_resume(payload: ComparisonRequest):
    if not payload.resume_text.strip():
        raise HTTPException(status_code=422, detail="Resume text cannot be empty")
    return ComparisonResponse(
        candidate_status="evaluated",
        findings=[
            EvidenceItem(
                skill="Python / FastAPI",
                matched=True,
                evidence_citation="Resume Section: Technical Skills",
                uncertainty_flag=False
            )
        ],
        requires_human_review=True
    )
