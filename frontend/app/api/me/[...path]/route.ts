import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export const maxDuration = 60;

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const token = request.cookies.get("dotareframe_session")?.value;
  const response = await fetch(`${API_BASE}/me/${path.join("/")}`, {
    method: request.method,
    headers: {
      "content-type": request.headers.get("content-type") ?? "application/json",
      ...(token ? { "x-session-token": token } : {})
    },
    body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
    cache: "no-store"
  });
  const body = await response.text();
  return new NextResponse(body, {
    status: response.status,
    headers: { "content-type": response.headers.get("content-type") ?? "application/json" }
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
