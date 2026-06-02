from pydantic import BaseModel, Field


class ReportCreateRequest(BaseModel):
    match_id: int = Field(gt=0)
    player_slot: int


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
