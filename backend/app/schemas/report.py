from typing import Literal, Optional

from pydantic import BaseModel, Field


class ReportCreateRequest(BaseModel):
    match_id: int = Field(gt=0)
    player_slot: int
    role: Optional[str] = None
    account_id: Optional[int] = Field(default=None, gt=0)


class ReportSummary(BaseModel):
    duration_minutes: int
    kda: str
    gpm: int
    xpm: int
    last_hits: int
    denies: int
    hero_damage: int
    tower_damage: int
    deaths: int


class Mistake(BaseModel):
    title: str
    what_happened: str
    evidence: list[str]
    confidence: Literal["low", "medium", "high"] = "medium"
    evidence_source: Literal["final_stats", "parsed_events", "cohort", "practical_target"] = "final_stats"
    why_it_matters: str
    try_next_game: str


class TimingNote(BaseModel):
    phase: str
    what_to_notice: str
    do_next_game: str


class PracticeDrill(BaseModel):
    title: str
    goal: str
    how_to_practice: str


class ComparisonContext(BaseModel):
    role: str
    hero: str
    duration_bucket: str
    rank_label: Optional[str] = None
    patch: Optional[str] = None
    baseline: str
    source: Literal["cohort", "practical_target"] = "practical_target"
    sample_size: int = 0


class BenchmarkMetric(BaseModel):
    metric: str
    label: str
    user_value: int
    comparison_value: int
    percentile: Optional[int] = None
    direction: Literal["higher", "lower"] = "higher"


class BenchmarkContext(BaseModel):
    source: Literal["cohort", "practical_target"]
    label: str
    sample_size: int
    metrics: list[BenchmarkMetric]


class NextMatchMission(BaseModel):
    title: str
    metric: Literal["deaths", "gpm", "tower_damage", "kill_participation"]
    target: int
    direction: Literal["at_most", "at_least"]
    explanation: str
    check_text: str


class TimelineEvent(BaseModel):
    minute: int = Field(ge=0)
    category: Literal["death", "item", "objective", "fight"]
    title: str
    detail: str
    tone: Literal["good", "warning", "risk", "info"] = "info"


class ProgressComparison(BaseModel):
    previous_report_id: str
    previous_match_id: int
    mission_title: str
    completed: bool
    previous_value: int
    current_value: int
    message: str


class ItemTimingCheckpoint(BaseModel):
    minute: int
    player_items: list[str]
    enemy_key_items: list[str]
    enemy_threats: list[str]
    player_answers: list[str]
    advice: str
    confidence: Literal["low", "medium", "high"] = "medium"
    evidence_source: Literal["parsed_events"] = "parsed_events"


class ItemTimingReview(BaseModel):
    main_lesson: str
    checkpoints: list[ItemTimingCheckpoint]
    next_match_item_lesson: str
    limitations: list[str] = Field(default_factory=list)


class CoachingReport(BaseModel):
    id: str
    match_id: int
    player_slot: int
    hero: str
    role: str
    result: str
    created_at: str
    summary: ReportSummary
    match_story: str
    main_problem: str
    main_evidence: list[str]
    performance_snapshot: dict[str, str]
    timing_notes: list[TimingNote]
    mistakes: list[Mistake]
    decision_rules: list[str]
    next_game_checklist: list[str]
    practice_drills: list[PracticeDrill]
    strengths: list[str]
    training_plan: list[str]
    match_evidence: list[str]
    confidence: str
    limitations: list[str]
    account_id: Optional[int] = None
    comparison_context: Optional[ComparisonContext] = None
    benchmark_context: Optional[BenchmarkContext] = None
    next_match_mission: Optional[NextMatchMission] = None
    timeline: list[TimelineEvent] = Field(default_factory=list)
    progress: Optional[ProgressComparison] = None
    item_timing_review: Optional[ItemTimingReview] = None
    summary_note: Optional[str] = None
    reflection_prompt: Optional[str] = None
    feedback: Optional[dict] = None


class ReportFeedbackRequest(BaseModel):
    helpful: bool
    reason: Optional[Literal["wrong_role", "weak_evidence", "too_generic", "hero_mismatch"]] = None


class SessionResponse(BaseModel):
    token: str
    profile: dict
