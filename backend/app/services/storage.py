import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from app.schemas.report import CoachingReport

DB_PATH = Path(__file__).resolve().parents[2] / "dotareframe.sqlite3"
DATABASE_URL = os.getenv("DATABASE_URL")


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def using_postgres() -> bool:
    return bool(DATABASE_URL)


@contextmanager
def postgres_connect() -> Iterator:
    if DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL is not configured")

    import psycopg

    with psycopg.connect(DATABASE_URL) as db:
        yield db


def init_db() -> None:
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


def save_report(report: CoachingReport) -> None:
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

    if using_postgres():
        with postgres_connect() as db:
            db.execute(
                """
                INSERT INTO reports (
                  id, match_id, player_slot, hero, result, created_at, kda, gpm,
                  main_problem, confidence, payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                  payload = EXCLUDED.payload
                """,
                values,
            )
        return

    with connect() as db:
        db.execute(
            """
            INSERT OR REPLACE INTO reports (
              id, match_id, player_slot, hero, result, created_at, kda, gpm,
              main_problem, confidence, payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )


def list_reports() -> list[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            rows = db.execute(
                """
                SELECT id, match_id, player_slot, hero, result, created_at, kda, gpm,
                       main_problem, confidence
                FROM reports
                ORDER BY created_at DESC
                """
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
            ORDER BY created_at DESC, rowid DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_report(report_id: str) -> Optional[dict]:
    init_db()
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute("SELECT payload FROM reports WHERE id = %s", (report_id,)).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    with connect() as db:
        row = db.execute("SELECT payload FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        return None
    return json.loads(row[0])
