import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export function GET(request: Request) {
  const origin = new URL(request.url).origin;
  const destination = new URL("/auth/steam/login", BACKEND_URL);
  destination.searchParams.set("return_to", `${origin}/match`);
  return NextResponse.redirect(destination);
}
