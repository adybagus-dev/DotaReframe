import type { CoachingReport, PlayerSummary, RecentMatch, SavedReportListItem } from "./types";

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
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        "content-type": "application/json",
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
  return apiJson<CoachingReport>("/reports", {
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
  return apiJson<SavedReportListItem[]>("/reports");
}

export async function getSavedReport(reportId: string): Promise<CoachingReport> {
  return apiJson<CoachingReport>(`/reports/${reportId}`);
}

export async function getRecentMatches(accountId: string): Promise<RecentMatch[]> {
  const data = await apiJson<{ matches: RecentMatch[] }>(`/players/${accountId}/recent-matches`);
  return data.matches;
}
