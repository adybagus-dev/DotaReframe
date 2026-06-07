import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function GET(request: NextRequest) {
  const origin = new URL(request.url).origin;
  const token = request.cookies.get("dotareframe_session")?.value;
  const response = await fetch(`${BACKEND_URL}/auth/steam/start`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(token ? { "x-session-token": token } : {})
    },
    body: JSON.stringify({ return_to: `${origin}/match` }),
    cache: "no-store"
  });
  if (!response.ok) return NextResponse.redirect(new URL("/match?steam_error=1", origin));
  const payload = (await response.json()) as { auth_url: string };
  return NextResponse.redirect(payload.auth_url);
}
