import json
import sqlite3
from pathlib import Path
from typing import Optional

from app.schemas.report import CoachingReport

DB_PATH = Path(__file__).resolve().parents[2] / "dotareframe.sqlite3"


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
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


def save_report(report: CoachingReport) -> None:
    init_db()
    payload = report.model_dump_json()
    with connect() as db:
        db.execute(
            """
            INSERT OR REPLACE INTO reports (
              id, match_id, player_slot, hero, result, created_at, kda, gpm,
              main_problem, confidence, payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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
            ),
        )


def list_reports() -> list[dict]:
    init_db()
    with connect() as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """
            SELECT id, match_id, player_slot, hero, result, created_at, kda, gpm,
                   main_problem, confidence
            FROM reports
            ORDER BY created_at DESC, rowid DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_report(report_id: str) -> Optional[dict]:
    init_db()
    with connect() as db:
        row = db.execute("SELECT payload FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        return None
    return json.loads(row[0])
