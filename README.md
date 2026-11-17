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


```

## Running VeriTalent AI Locally
VeriTalent AI is an AI-assisted technical applicant screening prototype built with Next.js, FastAPI, and Google Gemini. The following instructions explain how to install and run the Alpha release locally.

### Prerequisites
Before running the application, make sure you have:

- **Python 3.11 or newer**
- **Node.js and npm**
- **A Google Gemini API key**
- **Git** (optional if downloading the project as a ZIP file)

### 1. Configure the Google Gemini API Key
VeriTalent AI uses Google Gemini to analyze résumé information and identify documented technical skills. A valid API key is required to use the AI comparison feature.

1. Visit https://aistudio.google.com/apikey.
2. Sign in and obtain a Gemini API key.
3. Open the main VeriTalent AI project folder, where `README.md` and `pytest.ini` are located.
4. Create a file named `.env`.
5. Add the following line, replacing the placeholder with your actual API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

6. Save the `.env` file.

**Important:** Keep your API key private. Never upload your `.env` file or actual API key to GitHub.

### 2. Install and Start the Backend
Open a terminal in the main VeriTalent AI project folder.

**Create a Python virtual environment:**

```powershell
python -m venv .venv
```

**Activate the virtual environment:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Install the backend dependencies:**

```powershell
python -m pip install -r backend/requirements.txt
```

**Start the FastAPI backend:**

```powershell
python -m uvicorn backend.app.main:app --reload
```

The backend should start at:

http://127.0.0.1:8000

API documentation is available at:

http://127.0.0.1:8000/docs

**Leave this terminal running while using the application.**

### 3. Install and Start the Frontend
Open a **second terminal** in the main project folder.

**Navigate to the frontend directory:**

```powershell
cd frontend
```

**Install the frontend dependencies:**

```powershell
npm install
```

**Start the Next.js frontend:**

```powershell
npm run dev
```

Open your browser and navigate to:

http://localhost:3000

**Leave this terminal running while using the application.**

### 4. Test the Application
Once both servers are running:

1. Open VeriTalent AI at http://localhost:3000.
2. Enter a job description.
3. Enter the required technical skills, separated by commas or new lines.
4. Upload a synthetic PDF résumé or select **Paste résumé text** to enter synthetic résumé information.
5. Click **Compare technical skills**.
6. Review the AI-generated comparison results.

The application evaluates each required skill and reports whether supporting evidence was found in the résumé.

**PDF Requirements:**

- Maximum file size: **5 MB**
- Maximum document length: **4 pages**
- Scanned or encrypted PDFs may not be supported.

### 5. Understanding the Results
The comparison results include:

- **Documented:** Supporting evidence for the skill was identified in the résumé.
- **Not documented:** Supporting evidence for the skill was not identified.
- **Supporting evidence:** Relevant résumé information used to support a finding, when available.
- **AI uncertainty warnings:** Notifications that findings require manual verification.
- **Human review requirement:** A reminder that a person must review the AI-generated findings.

**Important:** A skill marked "Not documented" does not necessarily mean the applicant lacks that skill. It only means supporting evidence was not identified in the submitted résumé.

AI-generated findings may contain inaccuracies and should always be reviewed by a person.

### 6. Troubleshooting
**AI evaluation is temporarily unavailable**

If the application displays this message:

1. Confirm that the `.env` file exists in the main project folder.
2. Verify that `GEMINI_API_KEY` contains a valid Google Gemini API key, not the placeholder text.
3. Restart the FastAPI backend after changing the `.env` file.
4. Confirm that the backend is running at http://127.0.0.1:8000.
5. Check the backend terminal for additional error information.

**Frontend does not load**

1. Confirm that Node.js and npm are installed.
2. Verify that `npm install` completed.
3. Confirm that `npm run dev` is running.
4. Open http://localhost:3000.

**PDF upload fails**

1. Confirm that the file is a valid PDF.
2. Check that the PDF does not exceed **5 MB or 4 pages**.
3. Use a text-based PDF rather than a scanned document.
4. Verify that the PDF is not encrypted.

### 7. Alpha Release Limitations
VeriTalent AI is a prototype intended for demonstration and testing.

- Use **synthetic applicant information only**.
- AI-generated findings may contain errors and require **human verification**.
- The application is **not intended for real hiring decisions**.
- A valid **Google Gemini API key** is required to run AI comparisons.
- These installation instructions are intended for **Windows PowerShell**.

