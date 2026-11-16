import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const MAX_REQUEST_BYTES = 8388608;

export async function POST(request: NextRequest) {
  const base = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const declaredSize = Number(request.headers.get("content-length") || 0);
  if (declaredSize > MAX_REQUEST_BYTES) {
    return NextResponse.json({ detail: "Request is too large." }, { status: 413 });
  }
  try {
    const body = await request.text();
    if (Buffer.byteLength(body, "utf8") > MAX_REQUEST_BYTES) {
      return NextResponse.json({ detail: "Request is too large." }, { status: 413 });
    }
    try { JSON.parse(body); } catch {
      return NextResponse.json({ detail: "Invalid JSON request." }, { status: 400 });
    }
    const response = await fetch(`${base}/api/v1/compare-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(60000),
    });
    const result = await response.text();
    return new NextResponse(result, {
      status: response.status,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { detail: "The backend is unavailable or the request timed out. Confirm FastAPI and BACKEND_URL are configured." },
      { status: 503, headers: { "Cache-Control": "no-store" } }
    );
  }
}
