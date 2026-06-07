import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  if (!code) return NextResponse.redirect(new URL("/match?steam_error=1", request.url));
  const response = await fetch(`${BACKEND_URL}/auth/steam/exchange`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ code }),
    cache: "no-store"
  });
  if (!response.ok) return NextResponse.redirect(new URL("/match?steam_error=1", request.url));
  const payload = (await response.json()) as { token: string };
  const redirect = NextResponse.redirect(new URL("/match?steam_connected=1", request.url));
  redirect.cookies.set("dotareframe_session", payload.token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24 * 90,
    path: "/"
  });
  return redirect;
}
