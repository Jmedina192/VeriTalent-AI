export type EvidenceItem = { skill: string; matched: boolean; evidence_citation: string | null; uncertainty_flag: boolean };
export type ComparisonResponse = { candidate_status: "evaluated" | "mock_scaffold" | "error"; findings: EvidenceItem[]; requires_human_review: boolean };
export type ComparisonRequest = { job_description: string; resume_text: string; required_skills: string[] };
export type PdfComparisonRequest = { job_description: string; pdf_base64: string; required_skills: string[] };
