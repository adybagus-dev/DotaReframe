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

export async function createOrGetReport(matchId: string, playerSlot: string, role?: string): Promise<CoachingReport> {
  const data = await safeJson<CoachingReport>("/reports", {
    method: "POST",
    body: JSON.stringify({
      match_id: Number(matchId),
      player_slot: Number(playerSlot),
      role
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
  const profile = roleProfile(report.role);
  const isSupport = report.role === "Soft Support" || report.role === "Hard Support";
  const targetDeaths = Math.max(3, Math.min(profile.deaths, report.summary.deaths - 2));
  const targetGpm = isSupport ? profile.gpm : Math.max(profile.gpm, report.summary.gpm + 20);
  const targetTowerDamage = isSupport ? profile.towerDamage : Math.max(profile.towerDamage, report.summary.tower_damage + 400);
  const resultNoun = report.result === "Won" ? "win" : "loss";
  const rolePhrase = report.role && report.role !== "Unknown Role" ? ` as ${report.role}` : "";

  return {
    ...report,
    match_story:
      report.match_story ??
      `You played ${report.hero}${rolePhrase} and finished ${report.summary.kda} in a ${report.summary.duration_minutes}-minute ${resultNoun}. I am judging the stats against ${report.role} expectations, so ${report.summary.gpm} GPM is compared to about ${profile.gpm} GPM. The useful clue is the mix of ${report.summary.deaths} deaths and ${report.summary.tower_damage} tower damage.`,
    timing_notes:
      report.timing_notes ?? [
        {
          phase: "0-10 min",
          what_to_notice: `Your final GPM was ${report.summary.gpm}. For ${report.role}, a rough target is ${profile.gpm}.`,
          do_next_game: "Keep your lane job and safe resource pattern connected. Skip far fights unless they protect a tower, rune, Roshan, or core hero."
        },
        {
          phase: "10-25 min",
          what_to_notice: `You finished with ${report.summary.deaths} deaths. For ${report.role}, the rough danger line is ${profile.deaths}.`,
          do_next_game: "Join fights that defend a tower, secure Roshan, save your core, or happen beside your team's path."
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
        `Judge your stats as ${report.role}: about ${profile.gpm} GPM is a useful resource target, not a universal carry number.`,
        "Join a fight before your timing only if it protects your tower, secures Roshan, saves your core, or happens beside your team's path.",
        "If two or more enemy heroes are missing and your team has no vision, do not walk into the next dark area first.",
        "After a won fight, choose one objective within 5 seconds: tower, Roshan, enemy jungle, or lane shove.",
        `If your deaths reach ${targetDeaths} before 25 minutes next game, slow down and farm closer to vision.`
      ],
    next_game_checklist:
      report.next_game_checklist ?? [
        `Play the next match as ${report.role} and keep deaths at ${targetDeaths} or lower.`,
        isSupport
          ? `Keep support resources healthy: around ${targetGpm}+ GPM from pulls, stacks, runes, and unused waves, without stealing core farm.`
          : `Reach at least ${targetGpm} GPM for this role.`,
        isSupport
          ? "Help take at least two objectives through vision, saves, tower hits, or guarding the hero hitting buildings."
          : `Create at least ${targetTowerDamage} tower damage or clearly help take two objectives.`,
        "Skip at least one fight that is far from your job and does not defend a tower, rune, Roshan, or core hero.",
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

function roleProfile(role: string) {
  if (role === "Carry") return { gpm: 560, deaths: 6, towerDamage: 2500 };
  if (role === "Mid") return { gpm: 500, deaths: 6, towerDamage: 1800 };
  if (role === "Offlane") return { gpm: 430, deaths: 7, towerDamage: 1400 };
  if (role === "Soft Support") return { gpm: 300, deaths: 8, towerDamage: 700 };
  if (role === "Hard Support") return { gpm: 260, deaths: 8, towerDamage: 500 };
  return { gpm: 430, deaths: 7, towerDamage: 1400 };
}
