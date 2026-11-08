# VeriTalent AI

AI-assisted technical applicant screening platform built with Next.js, FastAPI, PostgreSQL/pgvector, and Google Gemini (CMSC 495 Capstone - Group 4).

## Team Members & Roles
* **Julio Medina** – Lead Architect (Backend API, Database/pgvector, Repository & Infrastructure)
* **Brian Marquez** – Interface Designer (Next.js Frontend UI, Recruiter Workflows, Client Validation)
* **Karen Miller** – Integration Lead (Google Gemini Prompts, Structured Outputs, Preprocessing & Evaluation)

## Repository Folder Structure
```text
VeriTalent-AI/
├── backend/                  # FastAPI backend & Gemini integration
│   ├── app/
│   │   ├── api/              # REST route endpoints
│   │   ├── core/             # Config, environment variables, security
│   │   ├── models/           # Pydantic schemas & database models
│   │   └── services/         # Gemini AI service, PDF extraction, pgvector queries
│   ├── tests/                # Backend & AI evaluation unit tests
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js recruiter web interface
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # UI components (upload forms, evidence viewer)
│   │   └── types/            # TypeScript API contracts
│   └── package.json
├── db/                       # PostgreSQL & pgvector initialization scripts
│   └── init.sql
├── data/                     # Synthetic resumes, job descriptions, & evaluation sets
└── README.md
