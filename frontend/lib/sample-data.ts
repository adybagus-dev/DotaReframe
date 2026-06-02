import type { CoachingReport, MatchSummary, SavedReportListItem } from "./types";

export const sampleMatch: MatchSummary = {
  match_id: 8123456789,
  duration_minutes: 42,
  radiant_result: "Lost",
  dire_result: "Won",
  players: [
    { match_id: 8123456789, player_slot: 0, hero: "Juggernaut", team: "Radiant", result: "Lost", role: "Safe Lane", kda: "8 / 7 / 11", gpm: 512 },
    { match_id: 8123456789, player_slot: 1, hero: "Crystal Maiden", team: "Radiant", result: "Lost", role: "Hard Support", kda: "2 / 9 / 19", gpm: 291 },
    { match_id: 8123456789, player_slot: 2, hero: "Pudge", team: "Radiant", result: "Lost", role: "Off Lane", kda: "10 / 8 / 12", gpm: 405 },
    { match_id: 8123456789, player_slot: 3, hero: "Lina", team: "Radiant", result: "Lost", role: "Mid Lane", kda: "6 / 6 / 8", gpm: 468 },
    { match_id: 8123456789, player_slot: 4, hero: "Tidehunter", team: "Radiant", result: "Lost", role: "Off Lane", kda: "3 / 5 / 17", gpm: 371 },
    { match_id: 8123456789, player_slot: 128, hero: "Phantom Assassin", team: "Dire", result: "Won", role: "Safe Lane", kda: "15 / 4 / 10", gpm: 658 },
    { match_id: 8123456789, player_slot: 129, hero: "Lion", team: "Dire", result: "Won", role: "Support", kda: "4 / 8 / 20", gpm: 322 },
    { match_id: 8123456789, player_slot: 130, hero: "Sniper", team: "Dire", result: "Won", role: "Mid Lane", kda: "12 / 3 / 14", gpm: 602 },
    { match_id: 8123456789, player_slot: 131, hero: "Dazzle", team: "Dire", result: "Won", role: "Hard Support", kda: "1 / 5 / 24", gpm: 315 },
    { match_id: 8123456789, player_slot: 132, hero: "Axe", team: "Dire", result: "Won", role: "Off Lane", kda: "7 / 6 / 18", gpm: 429 }
  ]
};

export const sampleReport: CoachingReport = {
  id: "report-8123456789-0",
  match_id: 8123456789,
  player_slot: 0,
  hero: "Juggernaut",
  role: "Safe Lane",
  result: "Lost",
  created_at: "2026-06-01",
  summary: {
    duration_minutes: 42,
    kda: "8 / 7 / 11",
    gpm: 512,
    xpm: 641,
    last_hits: 286,
    denies: 12,
    hero_damage: 24100,
    tower_damage: 1240,
    deaths: 7
  },
  match_story:
    "You played Juggernaut as Safe Lane and finished 8 / 7 / 11 in a 42-minute loss. Your late-game fights were useful, but the game was harder because your early deaths slowed your farming item and your kills did not become enough tower damage. The fix is not to avoid every fight. The fix is to choose fights that protect your timing or turn into objectives.",
  main_problem: "You fought too early before your farming item.",
  main_evidence: ["3 deaths before minute 18", "Battle Fury finished at 17:42"],
  performance_snapshot: {
    farming: "Needs Work",
    fighting: "Good",
    survival: "Needs Work",
    objectives: "Low Impact"
  },
  timing_notes: [
    {
      phase: "0-10 min",
      what_to_notice: "Your lane should set up safe farm into nearby camps.",
      do_next_game: "Keep lane and jungle connected. Skip far fights unless your tower is dying."
    },
    {
      phase: "10-25 min",
      what_to_notice: "This is where optional fights delayed your strongest timing.",
      do_next_game: "Only join fights that defend a tower, secure Roshan, or happen beside your farming path."
    },
    {
      phase: "After won fights",
      what_to_notice: "Tower damage ended at 1240, so kills did not become enough map pressure.",
      do_next_game: "Look at the closest lane first. If it is near a tower, hit the tower before farming your own jungle."
    },
    {
      phase: "Late game",
      what_to_notice: "Unsafe deaths get more expensive when death timers are long.",
      do_next_game: "Do not enter fog first. Let a tankier hero or a ward check the area before you commit."
    }
  ],
  mistakes: [
    {
      title: "Fought before your item timing",
      what_happened: "You joined fights before your first core item was ready.",
      evidence: ["3 deaths before minute 18", "Battle Fury finished at 17:42"],
      why_it_matters: "As a carry, dying before your farming item delays your strongest timing.",
      try_next_game: "Farm safer until your first core item, unless your team is defending a tower."
    },
    {
      title: "Farming slowed after minute 10",
      what_happened: "Your gold growth dropped when you started joining optional fights.",
      evidence: ["Farming slowed after minute 10", "GPM finished at 512"],
      why_it_matters: "Juggernaut needs steady gold before he can take over fights.",
      try_next_game: "Only join early fights when they protect your tower or secure a clear objective."
    },
    {
      title: "Kills did not become towers",
      what_happened: "Your team got kills, but your tower damage stayed low.",
      evidence: ["Tower damage: 1240", "Hero damage: 24100"],
      why_it_matters: "Kills matter more when they lead to towers, Roshan, or enemy jungle control.",
      try_next_game: "After every won fight, immediately check if you can hit a tower or take enemy camps."
    }
  ],
  decision_rules: [
    "Join a fight before your item timing only if it protects your tower, secures Roshan, or happens beside your farming path.",
    "If two or more enemy heroes are missing and your team has no vision, do not walk into the next dark area first.",
    "After a won fight, choose one objective within 5 seconds: tower, Roshan, enemy jungle, or lane shove.",
    "If you die 5 times before 25 minutes next game, slow down and farm closer to vision."
  ],
  next_game_checklist: [
    "Keep deaths at 5 or lower.",
    "Reach at least 540 GPM if you play a farming core.",
    "Deal at least 2000 tower damage or help take two clear objectives.",
    "Skip at least one fight that is far from your farm and does not defend a tower.",
    "After each death, write one sentence: what made that area unsafe?"
  ],
  practice_drills: [
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
        "Pause after each death and name the missing information: no ward, missing enemy hero, no teammate nearby, or overstay."
    }
  ],
  strengths: ["Good late-game teamfight participation", "Solid last-hit count by the end of the match"],
  training_plan: [
    "For the next 3 games, focus on reaching your first farming item before joining optional fights.",
    "After every won fight, check if your team can take a tower, Roshan, or enemy jungle.",
    "When you die, ask whether that area was safe before walking back there again."
  ],
  match_evidence: ["Duration: 42 minutes", "KDA: 8 / 7 / 11", "GPM: 512", "XPM: 641", "Last hits: 286", "Tower damage: 1240"],
  confidence: "medium",
  limitations: ["This review is based on match stats and may not fully understand positioning, voice calls, or team strategy."]
};

export const savedReports: SavedReportListItem[] = [
  {
    id: sampleReport.id,
    match_id: sampleReport.match_id,
    player_slot: sampleReport.player_slot,
    hero: sampleReport.hero,
    result: sampleReport.result,
    created_at: sampleReport.created_at,
    kda: sampleReport.summary.kda,
    gpm: sampleReport.summary.gpm,
    main_problem: sampleReport.main_problem,
    confidence: sampleReport.confidence
  },
  {
    id: "report-8123456789-1",
    match_id: 8123456789,
    player_slot: 1,
    hero: "Crystal Maiden",
    result: "Lost",
    created_at: "2026-06-01",
    kda: "2 / 9 / 19",
    gpm: 291,
    main_problem: "You died in unsafe areas while placing vision.",
    confidence: "medium"
  },
  {
    id: "report-8123456789-128",
    match_id: 8123456789,
    player_slot: 128,
    hero: "Phantom Assassin",
    result: "Won",
    created_at: "2026-06-01",
    kda: "15 / 4 / 10",
    gpm: 658,
    main_problem: "Good farming pace. Next, turn fights into towers faster.",
    confidence: "high"
  }
];

export function getReportById(id: string): CoachingReport {
  if (id === sampleReport.id) return sampleReport;
  const item = savedReports.find((report) => report.id === id);
  return {
    ...sampleReport,
    id,
    player_slot: item?.player_slot ?? sampleReport.player_slot,
    hero: item?.hero ?? sampleReport.hero,
    result: item?.result ?? sampleReport.result,
    main_problem: item?.main_problem ?? sampleReport.main_problem,
    confidence: item?.confidence ?? sampleReport.confidence,
    summary: {
      ...sampleReport.summary,
      kda: item?.kda ?? sampleReport.summary.kda,
      gpm: item?.gpm ?? sampleReport.summary.gpm
    }
  };
}

export function getReportForPlayer(matchId: string, playerSlot: string): CoachingReport {
  const player = sampleMatch.players.find((candidate) => String(candidate.player_slot) === playerSlot);
  return {
    ...sampleReport,
    id: `report-${matchId}-${playerSlot}`,
    match_id: Number(matchId),
    player_slot: Number(playerSlot),
    hero: player?.hero ?? sampleReport.hero,
    role: player?.role ?? sampleReport.role,
    result: player?.result ?? sampleReport.result,
    summary: {
      ...sampleReport.summary,
      kda: player?.kda ?? sampleReport.summary.kda,
      gpm: player?.gpm ?? sampleReport.summary.gpm
    }
  };
}
