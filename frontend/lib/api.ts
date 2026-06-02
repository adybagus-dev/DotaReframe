import { getReportById, getReportForPlayer, sampleMatch, savedReports } from "./sample-data";
import type { CoachingReport, PlayerSummary, SavedReportListItem } from "./types";

const API_BASE = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

async function safeJson<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        "content-type": "application/json",
        ...(init?.headers ?? {})
      }
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getPlayers(matchId: string): Promise<PlayerSummary[]> {
  const data = await safeJson<{ players: PlayerSummary[] }>(`/matches/${matchId}/players`);
  if (data?.players?.length) return data.players;
  return sampleMatch.players.map((player) => ({ ...player, match_id: Number(matchId) }));
}

export async function createOrGetReport(matchId: string, playerSlot: string): Promise<CoachingReport> {
  const data = await safeJson<CoachingReport>("/reports", {
    method: "POST",
    body: JSON.stringify({
      match_id: Number(matchId),
      player_slot: Number(playerSlot)
    })
  });
  return enrichReport(data ?? getReportForPlayer(matchId, playerSlot));
}

export async function getSavedReports(): Promise<SavedReportListItem[]> {
  const data = await safeJson<SavedReportListItem[]>("/reports");
  return data?.length ? data : savedReports;
}

export async function getSavedReport(reportId: string): Promise<CoachingReport> {
  const data = await safeJson<CoachingReport>(`/reports/${reportId}`);
  return enrichReport(data ?? getReportById(reportId));
}

function enrichReport(report: CoachingReport): CoachingReport {
  const targetDeaths = Math.max(3, report.summary.deaths - 2);
  const targetGpm = Math.max(520, report.summary.gpm + 30);
  const targetTowerDamage = Math.max(2000, report.summary.tower_damage + 800);
  const resultNoun = report.result === "Won" ? "win" : "loss";
  const rolePhrase = report.role && report.role !== "Unknown Role" ? ` as ${report.role}` : "";

  return {
    ...report,
    match_story:
      report.match_story ??
      `You played ${report.hero}${rolePhrase} and finished ${report.summary.kda} in a ${report.summary.duration_minutes}-minute ${resultNoun}. The useful clue is the mix of ${report.summary.deaths} deaths and ${report.summary.tower_damage} tower damage. The next step is to choose fights that protect your timing or turn into objectives.`,
    timing_notes:
      report.timing_notes ?? [
        {
          phase: "0-10 min",
          what_to_notice: `Your final GPM was ${report.summary.gpm}. Good games start with a stable first farming pattern.`,
          do_next_game: "Keep lane and nearby camps connected. Skip far fights unless your tower is dying."
        },
        {
          phase: "10-25 min",
          what_to_notice: `You finished with ${report.summary.deaths} deaths. Optional fights can make the next item late.`,
          do_next_game: "Join fights that defend a tower, secure Roshan, or happen beside your farming path."
        },
        {
          phase: "After won fights",
          what_to_notice: `Tower damage ended at ${report.summary.tower_damage}. This shows how much pressure became buildings.`,
          do_next_game: "After a won fight, look at the closest lane first. If it is near a tower, hit the tower."
        },
        {
          phase: "Late game",
          what_to_notice: "One unsafe death can decide the map when death timers are long.",
          do_next_game: "Do not enter fog first. Let a tankier hero or a ward check the area before you commit."
        }
      ],
    decision_rules:
      report.decision_rules ?? [
        "Join a fight before your item timing only if it protects your tower, secures Roshan, or happens beside your farming path.",
        "If two or more enemy heroes are missing and your team has no vision, do not walk into the next dark area first.",
        "After a won fight, choose one objective within 5 seconds: tower, Roshan, enemy jungle, or lane shove.",
        `If your deaths reach ${targetDeaths} before 25 minutes next game, slow down and farm closer to vision.`
      ],
    next_game_checklist:
      report.next_game_checklist ?? [
        `Keep deaths at ${targetDeaths} or lower.`,
        `Reach at least ${targetGpm} GPM if you play a farming core.`,
        `Deal at least ${targetTowerDamage} tower damage or clearly help take two objectives.`,
        "Skip at least one fight that is far from your farm and does not defend a tower.",
        "After each death, write one sentence: what made that area unsafe?"
      ],
    practice_drills:
      report.practice_drills ?? [
        {
          title: "Safe farm loop",
          goal: "Build a habit of farming without walking into dead areas.",
          how_to_practice:
            "For 10 minutes, repeat: push a safe wave, take one nearby camp, check minimap, then decide. Do not cross the river unless enemy heroes show or your team is with you."
        },
        {
          title: "Fight-to-objective check",
          goal: "Turn kills into something that helps win.",
          how_to_practice:
            "After every won fight, say out loud: tower, Roshan, enemy jungle, or reset. Pick one before farming your own jungle."
        },
        {
          title: "Death review",
          goal: "Reduce repeat deaths in the same unsafe areas.",
          how_to_practice:
            "After each death, name the missing information: no ward, missing enemy hero, no teammate nearby, or overstay."
        }
      ]
  };
}
