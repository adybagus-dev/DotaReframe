import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
const COOKIE_NAME = "dotareframe_session";

export async function middleware(request: NextRequest) {
  const existing = request.cookies.get(COOKIE_NAME)?.value;
  if (existing) return NextResponse.next();

  try {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      cache: "no-store"
    });
    if (!response.ok) return NextResponse.next();
    const payload = (await response.json()) as { token: string };
    const headers = new Headers(request.headers);
    headers.set("cookie", `${request.headers.get("cookie") ?? ""}; ${COOKIE_NAME}=${payload.token}`);
    const next = NextResponse.next({ request: { headers } });
    next.cookies.set(COOKIE_NAME, payload.token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 90,
      path: "/"
    });
    return next;
  } catch {
    return NextResponse.next();
  }
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
