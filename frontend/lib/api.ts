import { cookies } from "next/headers";
import type {
  CoachingReport,
  DashboardSummary,
  PlayerSummary,
  RecentMatch,
  ReportFeedback,
  ReviewContext,
  SavedReportListItem
} from "./types";

const API_BASE = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("dotareframe_session")?.value;
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        "content-type": "application/json",
        ...(sessionToken ? { "x-session-token": sessionToken } : {}),
        ...(init?.headers ?? {})
      }
    });
  } catch {
    throw new ApiError("DotaReframe could not reach the coaching server. Please try again.", 503);
  }

  if (!response.ok) {
    let message = "The request could not be completed. Please try again.";
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) message = payload.detail;
    } catch {
      // Keep the safe user-facing fallback.
    }
    throw new ApiError(message, response.status);
  }
  return (await response.json()) as T;
}

export async function getPlayers(matchId: string): Promise<PlayerSummary[]> {
  const data = await apiJson<{ players: PlayerSummary[] }>(`/matches/${matchId}/players`);
  return data.players;
}

export async function createOrGetReport(
  matchId: string,
  playerSlot: string,
  role?: string,
  accountId?: string
): Promise<CoachingReport> {
  return apiJson<CoachingReport>("/me/reports", {
    method: "POST",
    body: JSON.stringify({
      match_id: Number(matchId),
      player_slot: Number(playerSlot),
      role,
      account_id: accountId ? Number(accountId) : undefined
    })
  });
}

export async function getSavedReports(): Promise<SavedReportListItem[]> {
  return apiJson<SavedReportListItem[]>("/me/reports");
}

export async function getSavedReport(reportId: string): Promise<CoachingReport> {
  return apiJson<CoachingReport>(`/me/reports/${reportId}`);
}

export async function getRecentMatches(accountId: string): Promise<RecentMatch[]> {
  const data = await apiJson<{ matches: RecentMatch[] }>(`/players/${accountId}/recent-matches`);
  return data.matches;
}

export async function getDashboard(): Promise<DashboardSummary> {
  return apiJson<DashboardSummary>("/me/dashboard");
}

export async function getMyRecentMatches(): Promise<RecentMatch[]> {
  const data = await apiJson<{ matches: RecentMatch[] }>("/me/recent-matches");
  return data.matches;
}

export async function getReviewContext(matchId: string): Promise<ReviewContext> {
  return apiJson<ReviewContext>(`/me/matches/${matchId}/review-context`);
}

export async function saveReportFeedback(
  reportId: string,
  feedback: ReportFeedback
): Promise<ReportFeedback> {
  return apiJson<ReportFeedback>(`/me/reports/${reportId}/feedback`, {
    method: "PUT",
    body: JSON.stringify(feedback)
  });
}
