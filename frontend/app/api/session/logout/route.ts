import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  const token = request.cookies.get("dotareframe_session")?.value;
  const response = await fetch(`${BACKEND_URL}/sessions/logout`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(token ? { "x-session-token": token } : {})
    },
    cache: "no-store"
  });
  const payload = (await response.json()) as { token: string };
  const result = NextResponse.redirect(new URL("/match", request.url), 303);
  result.cookies.set("dotareframe_session", payload.token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 90,
    path: "/"
  });
  return result;
}
