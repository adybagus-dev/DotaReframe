import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Optional

from app.schemas.report import CoachingReport

DB_PATH = Path(__file__).resolve().parents[2] / "dotareframe.sqlite3"
SUPPORTED_DATABASE_MODES = {"sqlite", "postgres"}
MATCH_CACHE_TTL = timedelta(days=7)
_INIT_KEY: Optional[tuple[str, str]] = None


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def database_backend() -> str:
    mode = os.getenv("DATABASE_MODE", "sqlite").strip().lower()
    if mode not in SUPPORTED_DATABASE_MODES:
        raise RuntimeError("DATABASE_MODE must be either 'sqlite' or 'postgres'")
    return mode


def using_postgres() -> bool:
    return database_backend() == "postgres"


@contextmanager
def postgres_connect() -> Iterator:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required when DATABASE_MODE=postgres")

    import psycopg

    with psycopg.connect(database_url) as db:
        yield db


def init_db() -> None:
    global _INIT_KEY
    key = (database_backend(), os.getenv("DATABASE_URL", "") if using_postgres() else str(DB_PATH))
    if _INIT_KEY == key:
        return

    if using_postgres():
        with postgres_connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                  id TEXT PRIMARY KEY,
                  match_id INTEGER NOT NULL,
                  player_slot INTEGER NOT NULL,
                  hero TEXT NOT NULL,
                  result TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  kda TEXT NOT NULL,
                  gpm INTEGER NOT NULL,
                  main_problem TEXT NOT NULL,
                  confidence TEXT NOT NULL,
                  payload TEXT NOT NULL
                )
                """
            )
            for definition in (
                "profile_id TEXT",
                "account_id BIGINT",
                "role TEXT",
                "match_started_at BIGINT",
                "patch INTEGER",
                "rank_tier INTEGER",
                "duration_minutes INTEGER",
                "deaths INTEGER",
                "last_hits INTEGER",
                "hero_damage INTEGER",
                "tower_damage INTEGER",
                "healing INTEGER",
                "kill_participation INTEGER",
            ):
                db.execute(f"ALTER TABLE reports ADD COLUMN IF NOT EXISTS {definition}")
            db.execute("CREATE INDEX IF NOT EXISTS reports_profile_created_idx ON reports (profile_id, created_at DESC)")
            db.execute(
                "CREATE INDEX IF NOT EXISTS reports_profile_match_player_role_idx ON reports (profile_id, match_id, player_slot, role)"
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS report_feedback (
                  profile_id TEXT NOT NULL,
                  report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
                  helpful BOOLEAN NOT NULL,
                  reason TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  PRIMARY KEY (profile_id, report_id)
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS benchmark_samples (
                  report_id TEXT PRIMARY KEY REFERENCES reports(id) ON DELETE CASCADE,
                  hero TEXT NOT NULL,
                  role TEXT NOT NULL,
                  rank_bracket INTEGER,
                  duration_bucket TEXT NOT NULL,
                  patch INTEGER,
                  metrics TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS match_cache (
                  match_id BIGINT PRIMARY KEY,
                  payload TEXT NOT NULL,
                  fetched_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                )
                """
            )
        _INIT_KEY = key
        return

    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
              id TEXT PRIMARY KEY,
              match_id INTEGER NOT NULL,
              player_slot INTEGER NOT NULL,
              hero TEXT NOT NULL,
              result TEXT NOT NULL,
              created_at TEXT NOT NULL,
              kda TEXT NOT NULL,
              gpm INTEGER NOT NULL,
              main_problem TEXT NOT NULL,
              confidence TEXT NOT NULL,
              payload TEXT NOT NULL
            )
            """
        )
        existing = {row[1] for row in db.execute("PRAGMA table_info(reports)").fetchall()}
        for name, definition in (
            ("profile_id", "TEXT"),
            ("account_id", "INTEGER"),
            ("role", "TEXT"),
            ("match_started_at", "INTEGER"),
            ("patch", "INTEGER"),
            ("rank_tier", "INTEGER"),
            ("duration_minutes", "INTEGER"),
            ("deaths", "INTEGER"),
            ("last_hits", "INTEGER"),
            ("hero_damage", "INTEGER"),
            ("tower_damage", "INTEGER"),
            ("healing", "INTEGER"),
            ("kill_participation", "INTEGER"),
        ):
            if name not in existing:
                db.execute(f"ALTER TABLE reports ADD COLUMN {name} {definition}")
        db.execute("CREATE INDEX IF NOT EXISTS reports_profile_created_idx ON reports (profile_id, created_at DESC)")
        db.execute(
            "CREATE INDEX IF NOT EXISTS reports_profile_match_player_role_idx ON reports (profile_id, match_id, player_slot, role)"
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS report_feedback (
              profile_id TEXT NOT NULL,
              report_id TEXT NOT NULL,
              helpful INTEGER NOT NULL,
              reason TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              PRIMARY KEY (profile_id, report_id)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS match_cache (
              match_id INTEGER PRIMARY KEY,
              payload TEXT NOT NULL,
              fetched_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS benchmark_samples (
              report_id TEXT PRIMARY KEY,
              hero TEXT NOT NULL,
              role TEXT NOT NULL,
              rank_bracket INTEGER,
              duration_bucket TEXT NOT NULL,
              patch INTEGER,
              metrics TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
    _INIT_KEY = key


def save_report(report: CoachingReport, profile_id: Optional[str] = None, metrics: Optional[dict] = None) -> None:
    init_db()
    payload = report.model_dump_json()
    values = (
        report.id,
        report.match_id,
        report.player_slot,
        report.hero,
        report.result,
        report.created_at,
        report.summary.kda,
        report.summary.gpm,
        report.main_problem,
        report.confidence,
        payload,
    )
    metrics = metrics or {}
    extended = (
        profile_id,
        report.account_id,
        report.role,
        int(metrics.get("start_time") or 0) or None,
        metrics.get("patch"),
        metrics.get("rank_tier"),
        report.summary.duration_minutes,
        report.summary.deaths,
        report.summary.last_hits,
        report.summary.hero_damage,
        report.summary.tower_damage,
        int(metrics.get("healing") or 0),
        int(metrics.get("kill_participation") or 0),
    )

    if using_postgres():
        with postgres_connect() as db:
            db.execute(
                """
                INSERT INTO reports (
                  id, match_id, player_slot, hero, result, created_at, kda, gpm,
                  main_problem, confidence, payload, profile_id, account_id, role,
                  match_started_at, patch, rank_tier, duration_minutes, deaths, last_hits,
                  hero_damage, tower_damage, healing, kill_participation
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                  match_id = EXCLUDED.match_id,
                  player_slot = EXCLUDED.player_slot,
                  hero = EXCLUDED.hero,
                  result = EXCLUDED.result,
                  created_at = EXCLUDED.created_at,
                  kda = EXCLUDED.kda,
                  gpm = EXCLUDED.gpm,
                  main_problem = EXCLUDED.main_problem,
                  confidence = EXCLUDED.confidence,
                  payload = EXCLUDED.payload,
                  profile_id = COALESCE(EXCLUDED.profile_id, reports.profile_id),
                  account_id = EXCLUDED.account_id,
                  role = EXCLUDED.role,
                  match_started_at = EXCLUDED.match_started_at,
                  patch = EXCLUDED.patch,
                  rank_tier = EXCLUDED.rank_tier,
                  duration_minutes = EXCLUDED.duration_minutes,
                  deaths = EXCLUDED.deaths,
                  last_hits = EXCLUDED.last_hits,
                  hero_damage = EXCLUDED.hero_damage,
                  tower_damage = EXCLUDED.tower_damage,
                  healing = EXCLUDED.healing,
                  kill_participation = EXCLUDED.kill_participation
                """,
                values + extended,
            )
            _save_benchmark(db, report, metrics, postgres=True)
        return

    with connect() as db:
        db.execute(
            """
            INSERT OR REPLACE INTO reports (
              id, match_id, player_slot, hero, result, created_at, kda, gpm,
              main_problem, confidence, payload, profile_id, account_id, role,
              match_started_at, patch, rank_tier, duration_minutes, deaths, last_hits,
              hero_damage, tower_damage, healing, kill_participation
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            values + extended,
        )
        _save_benchmark(db, report, metrics, postgres=False)


def _save_benchmark(db, report: CoachingReport, metrics: dict, postgres: bool) -> None:
    rank_tier = metrics.get("rank_tier")
    rank_bracket = int(rank_tier) // 10 if rank_tier else None
    duration = report.summary.duration_minutes
    bucket = "under_30" if duration < 30 else "30_44" if duration < 45 else "45_plus"
    values = (
        report.id,
        report.hero,
        report.role,
        rank_bracket,
        bucket,
        metrics.get("patch"),
        json.dumps(
            {
                "gpm": report.summary.gpm,
                "deaths": report.summary.deaths,
                "last_hits": report.summary.last_hits,
                "hero_damage": report.summary.hero_damage,
                "tower_damage": report.summary.tower_damage,
                "healing": int(metrics.get("healing") or 0),
                "kill_participation": int(metrics.get("kill_participation") or 0),
                "wards_placed": int(metrics.get("wards_placed") or 0),
                "camps_stacked": int(metrics.get("camps_stacked") or 0),
            }
        ),
        report.created_at,
    )
    if postgres:
        db.execute(
            """
            INSERT INTO benchmark_samples (report_id,hero,role,rank_bracket,duration_bucket,patch,metrics,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (report_id) DO UPDATE SET metrics=EXCLUDED.metrics, created_at=EXCLUDED.created_at
            """,
            values,
        )
    else:
        db.execute(
            "INSERT OR REPLACE INTO benchmark_samples (report_id,hero,role,rank_bracket,duration_bucket,patch,metrics,created_at) VALUES (?,?,?,?,?,?,?,?)",
            values,
        )


def list_reports(profile_id: Optional[str] = None) -> list[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            rows = db.execute(
                """
                SELECT id, match_id, player_slot, hero, result, created_at, kda, gpm,
                       main_problem, confidence
                FROM reports
                WHERE profile_id = %s
                ORDER BY match_started_at DESC NULLS LAST, created_at DESC
                """,
                (profile_id,),
            ).fetchall()
        columns = ["id", "match_id", "player_slot", "hero", "result", "created_at", "kda", "gpm", "main_problem", "confidence"]
        return [dict(zip(columns, row)) for row in rows]

    with connect() as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """
            SELECT id, match_id, player_slot, hero, result, created_at, kda, gpm,
                   main_problem, confidence
            FROM reports
            WHERE profile_id = ?
            ORDER BY match_started_at DESC, created_at DESC, rowid DESC
            """,
            (profile_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_report(report_id: str, profile_id: Optional[str] = None) -> Optional[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute("SELECT payload FROM reports WHERE id = %s AND profile_id = %s", (report_id, profile_id)).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    with connect() as db:
        row = db.execute("SELECT payload FROM reports WHERE id = ? AND profile_id = ?", (report_id, profile_id)).fetchone()
    if row is None:
        return None
    return json.loads(row[0])


def list_report_payloads(limit: int = 50, profile_id: Optional[str] = None) -> list[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            rows = db.execute(
                "SELECT payload FROM reports WHERE profile_id = %s ORDER BY match_started_at DESC NULLS LAST, created_at DESC LIMIT %s",
                (profile_id, limit),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    with connect() as db:
        rows = db.execute(
            "SELECT payload FROM reports WHERE profile_id = ? ORDER BY match_started_at DESC, created_at DESC, rowid DESC LIMIT ?",
            (profile_id, limit),
        ).fetchall()
    return [json.loads(row[0]) for row in rows]


def find_duplicate_report(profile_id: str, match_id: int, player_slot: int, role: str) -> Optional[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute(
                "SELECT payload FROM reports WHERE profile_id=%s AND match_id=%s AND player_slot=%s AND role=%s LIMIT 1",
                (profile_id, match_id, player_slot, role),
            ).fetchone()
    else:
        with connect() as db:
            row = db.execute(
                "SELECT payload FROM reports WHERE profile_id=? AND match_id=? AND player_slot=? AND role=? LIMIT 1",
                (profile_id, match_id, player_slot, role),
            ).fetchone()
    return json.loads(row[0]) if row else None


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_cached_match(match_id: int, allow_stale: bool = False) -> Optional[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute("SELECT payload, fetched_at FROM match_cache WHERE match_id=%s", (match_id,)).fetchone()
    else:
        with connect() as db:
            row = db.execute("SELECT payload, fetched_at FROM match_cache WHERE match_id=?", (match_id,)).fetchone()
    if row is None:
        return None
    try:
        fetched_at = _parse_timestamp(row[1])
    except (TypeError, ValueError):
        fetched_at = datetime.fromtimestamp(0, timezone.utc)
    if not allow_stale and datetime.now(timezone.utc) - fetched_at > MATCH_CACHE_TTL:
        return None
    return json.loads(row[0])


def save_cached_match(match_id: int, payload: dict) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    values = (match_id, json.dumps(payload), now, now)
    if using_postgres():
        with postgres_connect() as db:
            db.execute(
                """
                INSERT INTO match_cache (match_id,payload,fetched_at,updated_at)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (match_id) DO UPDATE SET
                  payload=EXCLUDED.payload,
                  fetched_at=EXCLUDED.fetched_at,
                  updated_at=EXCLUDED.updated_at
                """,
                values,
            )
        return

    with connect() as db:
        db.execute(
            """
            INSERT INTO match_cache (match_id,payload,fetched_at,updated_at)
            VALUES (?,?,?,?)
            ON CONFLICT(match_id) DO UPDATE SET
              payload=excluded.payload,
              fetched_at=excluded.fetched_at,
              updated_at=excluded.updated_at
            """,
            values,
        )


def save_feedback(profile_id: str, report_id: str, helpful: bool, reason: Optional[str]) -> dict:
    from datetime import datetime, timezone

    init_db()
    if get_report(report_id, profile_id) is None:
        raise KeyError("Report not found")
    now = datetime.now(timezone.utc).isoformat()
    values = (profile_id, report_id, helpful if using_postgres() else int(helpful), reason, now, now)
    if using_postgres():
        with postgres_connect() as db:
            db.execute(
                """
                INSERT INTO report_feedback (profile_id,report_id,helpful,reason,created_at,updated_at)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (profile_id,report_id) DO UPDATE SET helpful=EXCLUDED.helpful,reason=EXCLUDED.reason,updated_at=EXCLUDED.updated_at
                """,
                values,
            )
    else:
        with connect() as db:
            db.execute(
                """
                INSERT INTO report_feedback (profile_id,report_id,helpful,reason,created_at,updated_at)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(profile_id,report_id) DO UPDATE SET helpful=excluded.helpful,reason=excluded.reason,updated_at=excluded.updated_at
                """,
                values,
            )
    return {"helpful": helpful, "reason": reason}


def get_feedback(profile_id: str, report_id: str) -> Optional[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute("SELECT helpful,reason FROM report_feedback WHERE profile_id=%s AND report_id=%s", (profile_id, report_id)).fetchone()
    else:
        with connect() as db:
            row = db.execute("SELECT helpful,reason FROM report_feedback WHERE profile_id=? AND report_id=?", (profile_id, report_id)).fetchone()
    return {"helpful": bool(row[0]), "reason": row[1]} if row else None


def get_benchmark_samples() -> list[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            rows = db.execute("SELECT hero,role,rank_bracket,duration_bucket,patch,metrics FROM benchmark_samples").fetchall()
    else:
        with connect() as db:
            rows = db.execute("SELECT hero,role,rank_bracket,duration_bucket,patch,metrics FROM benchmark_samples").fetchall()
    return [
        {"hero": row[0], "role": row[1], "rank_bracket": row[2], "duration_bucket": row[3], "patch": row[4], "metrics": json.loads(row[5])}
        for row in rows
    ]
