import { NextResponse } from "next/server";
import { ApiError, getRecentMatches } from "@/lib/api";

type RouteProps = {
  params: Promise<{ accountId: string }>;
};

export async function GET(_: Request, { params }: RouteProps) {
  const { accountId } = await params;
  try {
    return NextResponse.json({ matches: await getRecentMatches(accountId) });
  } catch (error) {
    const status = error instanceof ApiError ? error.status : 500;
    const message = error instanceof Error ? error.message : "Recent matches could not be loaded.";
    return NextResponse.json({ detail: message }, { status });
  }
}
