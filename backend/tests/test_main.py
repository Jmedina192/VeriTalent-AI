from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_compare_resume_valid_schema():
    payload = {
        "job_description": "Seeking a Python backend developer with FastAPI experience.",
        "resume_text": "Experienced software developer skilled in Python and FastAPI."
    }
    response = client.post("/api/v1/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_status"] == "mock_scaffold"
    assert data["requires_human_review"] is True
    assert "evidence_citation" in data["findings"][0]
    assert "uncertainty_flag" in data["findings"][0]

def test_compare_resume_rejects_short_input():
    payload = {"job_description": "short", "resume_text": "short"}
    response = client.post("/api/v1/compare", json=payload)
    assert response.status_code == 422

def test_compare_resume_rejects_whitespace_padding():
    payload = {
        "job_description": "               ",
        "resume_text": "     short     "
    }
    response = client.post("/api/v1/compare", json=payload)
    assert response.status_code == 422
