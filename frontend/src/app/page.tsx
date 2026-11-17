"use client";
import { useState, type FormEvent } from "react";
import type { ComparisonResponse } from "../types/api";

const MAX_SIZE = 5 * 1024 * 1024;
function skillsFromText(text: string): string[] { const seen = new Set<string>(); return text.split(/[,\n]/).map(s => s.trim()).filter(s => { const key = s.toLocaleLowerCase(); if (!key || seen.has(key)) return false; seen.add(key); return true; }); }
function errorText(detail: unknown): string { if (typeof detail === "string") return detail; if (Array.isArray(detail)) return detail.map((e: { msg?: string }) => e.msg || "Invalid input").join("; "); return "The request could not be completed."; }
function toBase64(file: File): Promise<string> { return new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => { const value = reader.result; if (typeof value !== "string") return reject(new Error("Could not read the file.")); resolve(value.split(",")[1] || ""); }; reader.onerror = () => reject(new Error("Could not read the file.")); reader.readAsDataURL(file); }); }
export default function Home() {
  const [mode, setMode] = useState<"pdf" | "text">("pdf");
  const [job, setJob] = useState(""); const [skills, setSkills] = useState(""); const [resume, setResume] = useState("");
  const [file, setFile] = useState<File | null>(null); const [busy, setBusy] = useState(false);
  const [error, setError] = useState(""); const [result, setResult] = useState<ComparisonResponse | null>(null);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setResult(null);
    if (job.trim().length < 10 || job.length > 10000) return setError("Job description must be 10–10,000 characters.");
    const required_skills = skillsFromText(skills);
    if (!required_skills.length) return setError("Enter at least one required skill, separated by commas or new lines.");
    if (mode === "text" && (resume.trim().length < 10 || resume.length > 25000)) return setError("Résumé text must be 10–25,000 characters.");
    if (mode === "pdf" && (!file || file.size === 0 || file.size > MAX_SIZE || (!file.name.toLowerCase().endsWith(".pdf")))) return setError("Select a nonempty PDF file no larger than 5 MB.");
    setBusy(true);
    try {
      const body = mode === "pdf" ? { job_description: job.trim(), required_skills, pdf_base64: await toBase64(file!) } : { job_description: job.trim(), required_skills, resume_text: resume.trim() };
      const response = await fetch(mode === "pdf" ? "/api/compare-pdf" : "/api/compare", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const payload: unknown = await response.json().catch(() => ({ detail: "The server returned an unreadable response." }));
      if (!response.ok) { const detail = (payload as { detail?: unknown }).detail; throw new Error(errorText(detail)); }
      if (!payload || typeof payload !== "object" || !Array.isArray((payload as ComparisonResponse).findings)) throw new Error("The backend returned an unexpected result format.");
      setResult(payload as ComparisonResponse);
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error."); }
    finally { setBusy(false); }
  }
  return <main className="shell"><header><div className="brand"><span className="logo">V</span><div><strong>VeriTalent-AI</strong><small>Technical applicant screening · Alpha release</small></div></div><span className="pill">Human-reviewed AI</span></header>
    <section className="hero"><p className="eyebrow">RECRUITER WORKSPACE</p><h1>Review technical skills with supporting evidence.</h1><p>Compare a résumé against job requirements. AI findings support recruiter judgment and are not automated hiring decisions.</p></section>
    <div className="layout"><form className="panel" onSubmit={submit}><h2>New comparison</h2><p className="muted">Complete the fields below to evaluate documented skills.</p>
      <label htmlFor="job">Job description</label><textarea id="job" rows={5} maxLength={10000} placeholder="Describe the position and its technical requirements..." value={job} onChange={e=>setJob(e.target.value)}/>
      <label htmlFor="skills">Required skills</label><textarea id="skills" rows={3} placeholder="Python, SQL, React" value={skills} onChange={e=>setSkills(e.target.value)}/><p className="hint">Separate skills with commas or new lines.</p>
      <div className="tabs" role="group" aria-label="Résumé input method"><button type="button" className={mode==="pdf"?"selected":""} onClick={()=>{setMode("pdf");setError("");setResult(null);}}>Upload PDF</button><button type="button" className={mode==="text"?"selected":""} onClick={()=>{setMode("text");setError("");setResult(null);}}>Paste résumé text</button></div>
      {mode === "pdf" ? <><label htmlFor="pdf">Applicant résumé (PDF)</label><input id="pdf" type="file" accept=".pdf,application/pdf" onChange={e=>{setFile(e.target.files?.[0]||null);setResult(null);setError("");}}/><p className="hint">Maximum 5 MB and 4 pages. Scanned or encrypted PDFs may not be supported. Files are sent to the configured backend for processing.</p></> : <><label htmlFor="resume">Applicant résumé text</label><textarea id="resume" rows={6} maxLength={25000} placeholder="Paste résumé content..." value={resume} onChange={e=>setResume(e.target.value)}/></>}
      {error && <div role="alert" className="error">{error}</div>}
      <button className="primary" type="submit" disabled={busy} aria-busy={busy}>{busy ? "Evaluating…" : "Compare technical skills"}</button>
      <p className="hint">Do not use this Alpha release for real hiring decisions. Use synthetic applicant information for testing.</p>
    </form><section className="panel results" aria-live="polite"><h2>Comparison results</h2>{busy && <p role="status" className="notice">Processing your comparison. This can take up to a minute.</p>}{!result ? <div className="empty"><div className="empty-icon">✦</div><h3>No comparison yet</h3><p>Submit a résumé and job requirements to view evidence-based findings here.</p></div> : <><div className="summary"><span className="pill">{result.candidate_status.replaceAll("_"," ")}</span><span>{result.findings.length} skill findings</span></div>{result.findings.map((finding,i)=><article className="finding" key={`${finding.skill}-${i}`}><div className="finding-head"><strong>{finding.skill}</strong><span className={finding.matched?"match":"unknown"}>{finding.matched?"Documented":"Not documented"}</span></div><p>{finding.evidence_citation || "No supporting evidence provided."}</p>{finding.uncertainty_flag && <small>AI uncertainty flagged — verify manually.</small>}</article>)}<div className="notice">{result.requires_human_review ? "Human review is required before interpreting these results." : "Human review is recommended for every result."}</div></>}</section></div>
    <footer>VeriTalent-AI · CMSC 495 Group 4 · Alpha prototype</footer></main>;
}
