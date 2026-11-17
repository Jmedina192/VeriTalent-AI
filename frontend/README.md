# VeriTalent-AI Frontend (Alpha)

Next.js App Router + TypeScript recruiter interface built to match `backend/app/main.py`.

## Start locally

Requires Node.js 20+ and Python with backend dependencies.

1. From the repository root, install backend dependencies: `python -m pip install -r backend/requirements.txt`.
2. Start FastAPI from the **repository root**: `python -m uvicorn backend.app.main:app --reload --port 8000`.
3. In a second terminal: `cd frontend && npm install`.
4. Copy `.env.example` to `.env.local`; set `BACKEND_URL` if your backend isn't on port 8000.
5. Run `npm run dev` and open `http://localhost:3000`.
6. Run `npm run typecheck` and `npm run build` before opening a pull request.

## Supported workflows

- Enter a job description (10–10,000 characters) and at least one unique required skill (comma/newline separated).
- Paste résumé text (10–25,000 characters) or upload a PDF (maximum 5 MiB and 4 pages, with server-side page validation).
- Submit to `POST /api/v1/compare` or `POST /api/v1/compare-pdf` via Next.js server-side proxy routes.
- Display the backend's `candidate_status`, evidence findings, uncertainty flags, and mandatory human-review notice.
- Show API validation errors and backend connection failures.

## Privacy and limits

The Next.js proxy uses the server-side `BACKEND_URL` environment variable and does not expose it to the browser. PDFs are Base64-encoded in the browser and sent to the local Next.js API, then forwarded to FastAPI. **No application database or file persistence is implemented by this frontend.** Avoid real applicant PII during Alpha testing. The backend's PII minimization does not guarantee removal of every sensitive detail.

## Testing / team review

1. Verify text résumé comparison with synthetic inputs and a configured Gemini API key.
2. Verify PDF comparison with a valid text-based PDF of four pages or fewer.
3. Confirm an oversized PDF is rejected client-side; confirm an over-four-page PDF is rejected server-side.
4. Confirm invalid job descriptions, missing skills, and backend-offline errors are displayed.
5. Confirm GitHub CI and end-to-end flows after integration. The existing GitHub workflow currently runs **backend Python tests only**; it must be expanded to check frontend builds if desired.

The backend requires a configured Gemini service for a successful live evaluation. Mocked tests do not prove a live AI response.

## Frontend GitHub Actions (optional but recommended)

Copy the included `frontend-ci.yml` to `.github/workflows/frontend-checks.yml` at the **repository root**. This adds a separate frontend typecheck/build workflow; it does not replace the existing backend Python tests. The workflow uses `npm install` because a lockfile is not included; after installing locally, commit `package-lock.json` and change the workflow to `npm ci` for reproducible builds.

## Integration caveats

The frontend cannot confirm PDF page count without parsing the PDF; the backend enforces the four-page maximum. Live Gemini behavior depends on a valid API key and service availability. The UI has no authentication or access control and is an academic Alpha prototype, not a production hiring application. Do not upload real applicant data.
