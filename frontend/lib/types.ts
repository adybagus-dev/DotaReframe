export type Team = "Radiant" | "Dire";
export type Result = "Won" | "Lost";
export type SnapshotValue = "Good" | "Needs Work" | "Low Impact" | "Okay";

export type PlayerSummary = {
  match_id: number;
  player_slot: number;
  hero: string;
  hero_image?: string;
  team: Team;
  result: Result;
  role?: string;
  kda: string;
  gpm: number;
};

export type MatchSummary = {
  match_id: number;
  duration_minutes: number;
  radiant_result: Result;
  dire_result: Result;
  players: PlayerSummary[];
};

export type Mistake = {
  title: string;
  what_happened: string;
  evidence: string[];
  confidence?: "low" | "medium" | "high";
  evidence_source?: "final_stats" | "parsed_events" | "cohort" | "practical_target";
  why_it_matters: string;
  try_next_game: string;
};

export type TimingNote = {
  phase: string;
  what_to_notice: string;
  do_next_game: string;
};

export type PracticeDrill = {
  title: string;
  goal: string;
  how_to_practice: string;
};

export type ComparisonContext = {
  role: string;
  hero: string;
  duration_bucket: string;
  rank_label?: string;
  patch?: string;
  baseline: string;
  source: "cohort" | "practical_target";
  sample_size: number;
};

export type BenchmarkMetric = {
  metric: string;
  label: string;
  user_value: number;
  comparison_value: number;
  percentile?: number | null;
  direction: "higher" | "lower";
};

export type BenchmarkContext = {
  source: "cohort" | "practical_target";
  label: string;
  sample_size: number;
  metrics: BenchmarkMetric[];
};

export type NextMatchMission = {
  title: string;
  metric: "deaths" | "gpm" | "tower_damage" | "kill_participation";
  target: number;
  direction: "at_most" | "at_least";
  explanation: string;
  check_text: string;
};

export type TimelineEvent = {
  minute: number;
  category: "death" | "item" | "objective" | "fight";
  title: string;
  detail: string;
  tone: "good" | "warning" | "risk" | "info";
};

export type ProgressComparison = {
  previous_report_id: string;
  previous_match_id: number;
  mission_title: string;
  completed: boolean;
  previous_value: number;
  current_value: number;
  message: string;
};

export type ItemTimingCheckpoint = {
  minute: number;
  player_items: string[];
  enemy_key_items: string[];
  enemy_threats: string[];
  player_answers: string[];
  advice: string;
  confidence: "low" | "medium" | "high";
  evidence_source: "parsed_events";
};

export type ItemTimingReview = {
  main_lesson: string;
  checkpoints: ItemTimingCheckpoint[];
  next_match_item_lesson: string;
  limitations: string[];
};

export type CoachingReport = {
  id: string;
  match_id: number;
  player_slot: number;
  hero: string;
  role: string;
  result: Result;
  created_at: string;
  summary: {
    duration_minutes: number;
    kda: string;
    gpm: number;
    xpm: number;
    last_hits: number;
    denies: number;
    hero_damage: number;
    tower_damage: number;
    deaths: number;
  };
  match_story?: string;
  main_problem: string;
  main_evidence: string[];
  performance_snapshot: {
    farming: SnapshotValue;
    fighting: SnapshotValue;
    survival: SnapshotValue;
    objectives: SnapshotValue;
  };
  timing_notes?: TimingNote[];
  mistakes: Mistake[];
  decision_rules?: string[];
  next_game_checklist?: string[];
  practice_drills?: PracticeDrill[];
  strengths: string[];
  training_plan: string[];
  match_evidence: string[];
  confidence: "low" | "medium" | "high";
  limitations: string[];
  account_id?: number;
  comparison_context?: ComparisonContext;
  benchmark_context?: BenchmarkContext;
  next_match_mission?: NextMatchMission;
  timeline?: TimelineEvent[];
  progress?: ProgressComparison;
  item_timing_review?: ItemTimingReview | null;
  feedback?: ReportFeedback;
  summary_note?: string | null;
  reflection_prompt?: string | null;
  is_latest?: boolean;
};

export type SavedReportListItem = {
  id: string;
  match_id: number;
  player_slot: number;
  hero: string;
  result: Result;
  created_at: string;
  kda: string;
  gpm: number;
  main_problem: string;
  confidence: "low" | "medium" | "high";
  summary_note?: string | null;
};

export type RecentMatch = {
  match_id: number;
  player_slot: number;
  hero: string;
  result: Result;
  kda: string;
  duration_minutes: number;
  started_at: number;
};

export type PlayerProfile = {
  id: string;
  steam_account_id?: number;
  is_guest: boolean;
};

export type ReportFeedback = {
  helpful: boolean;
  reason?: "wrong_role" | "weak_evidence" | "too_generic" | "hero_mismatch";
};

export type DashboardSummary = {
  profile: PlayerProfile;
  total_reports: number;
  mission_streak: number;
  active_mission?: NextMatchMission;
  latest_progress?: ProgressComparison;
  coach_note?: string;
  recent_reports: SavedReportListItem[];
};

export type ReviewContext = {
  match_id: number;
  detected_role: string;
  player: PlayerSummary;
};
