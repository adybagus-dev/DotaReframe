from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from app.services.storage import connect, postgres_connect, using_postgres

SESSION_DAYS = 90


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _token() -> str:
    return secrets.token_urlsafe(32)


def init_identity_db() -> None:
    boolean_type = "BOOLEAN" if using_postgres() else "INTEGER"
    statements = [
        f"""
        CREATE TABLE IF NOT EXISTS player_profiles (
          id TEXT PRIMARY KEY,
          steam_account_id BIGINT UNIQUE,
          is_guest {boolean_type} NOT NULL DEFAULT {'TRUE' if using_postgres() else '1'},
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sessions (
          id TEXT PRIMARY KEY,
          profile_id TEXT NOT NULL REFERENCES player_profiles(id) ON DELETE CASCADE,
          token_hash TEXT NOT NULL UNIQUE,
          expires_at TEXT NOT NULL,
          last_seen_at TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS steam_auth_states (
          state_hash TEXT PRIMARY KEY,
          profile_id TEXT NOT NULL REFERENCES player_profiles(id) ON DELETE CASCADE,
          return_to TEXT NOT NULL,
          expires_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS auth_exchanges (
          code_hash TEXT PRIMARY KEY,
          profile_id TEXT NOT NULL REFERENCES player_profiles(id) ON DELETE CASCADE,
          expires_at TEXT NOT NULL
        )
        """,
    ]
    if using_postgres():
        with postgres_connect() as db:
            for statement in statements:
                db.execute(statement)
    else:
        with connect() as db:
            db.execute("PRAGMA foreign_keys = ON")
            for statement in statements:
                db.execute(statement)
            exchange_columns = {row[1] for row in db.execute("PRAGMA table_info(auth_exchanges)").fetchall()}
            if "session_token" in exchange_columns:
                db.execute("DROP TABLE auth_exchanges")
                db.execute(
                    """
                    CREATE TABLE auth_exchanges (
                      code_hash TEXT PRIMARY KEY,
                      profile_id TEXT NOT NULL REFERENCES player_profiles(id) ON DELETE CASCADE,
                      expires_at TEXT NOT NULL
                    )
                    """
                )


def _row_dict(row, columns: list[str]) -> Optional[dict]:
    if row is None:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    return dict(zip(columns, row))


def create_session(profile_id: Optional[str] = None) -> tuple[str, dict]:
    init_identity_db()
    now = _now()
    if profile_id is None:
        profile_id = str(uuid4())
        profile_values = (profile_id, None, True, _iso(now), _iso(now))
        if using_postgres():
            with postgres_connect() as db:
                db.execute(
                    "INSERT INTO player_profiles (id, steam_account_id, is_guest, created_at, updated_at) VALUES (%s,%s,%s,%s,%s)",
                    profile_values,
                )
        else:
            with connect() as db:
                db.execute(
                    "INSERT INTO player_profiles (id, steam_account_id, is_guest, created_at, updated_at) VALUES (?,?,?,?,?)",
                    profile_values,
                )
    raw = _token()
    values = (str(uuid4()), profile_id, _hash(raw), _iso(now + timedelta(days=SESSION_DAYS)), _iso(now), _iso(now))
    if using_postgres():
        with postgres_connect() as db:
            db.execute(
                "INSERT INTO sessions (id, profile_id, token_hash, expires_at, last_seen_at, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
                values,
            )
    else:
        with connect() as db:
            db.execute(
                "INSERT INTO sessions (id, profile_id, token_hash, expires_at, last_seen_at, created_at) VALUES (?,?,?,?,?,?)",
                values,
            )
    profile = get_profile(profile_id)
    if profile is None:
        raise RuntimeError("Profile could not be created")
    return raw, profile


def get_profile(profile_id: str) -> Optional[dict]:
    columns = ["id", "steam_account_id", "is_guest", "created_at", "updated_at"]
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute(
                "SELECT id, steam_account_id, is_guest, created_at, updated_at FROM player_profiles WHERE id = %s",
                (profile_id,),
            ).fetchone()
    else:
        with connect() as db:
            db.row_factory = __import__("sqlite3").Row
            row = db.execute(
                "SELECT id, steam_account_id, is_guest, created_at, updated_at FROM player_profiles WHERE id = ?",
                (profile_id,),
            ).fetchone()
    profile = _row_dict(row, columns)
    if profile:
        profile["is_guest"] = bool(profile["is_guest"])
    return profile


def resolve_session(raw_token: Optional[str], touch: bool = True) -> Optional[dict]:
    if not raw_token:
        return None
    init_identity_db()
    columns = ["session_id", "profile_id", "expires_at"]
    query = """
        SELECT sessions.id, sessions.profile_id, sessions.expires_at
        FROM sessions WHERE sessions.token_hash = {placeholder}
    """
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute(query.format(placeholder="%s"), (_hash(raw_token),)).fetchone()
    else:
        with connect() as db:
            row = db.execute(query.format(placeholder="?"), (_hash(raw_token),)).fetchone()
    session = _row_dict(row, columns)
    if not session or datetime.fromisoformat(session["expires_at"]) <= _now():
        return None
    if touch:
        expiry = _iso(_now() + timedelta(days=SESSION_DAYS))
        seen = _iso(_now())
        if using_postgres():
            with postgres_connect() as db:
                db.execute("UPDATE sessions SET expires_at=%s,last_seen_at=%s WHERE id=%s", (expiry, seen, session["session_id"]))
        else:
            with connect() as db:
                db.execute("UPDATE sessions SET expires_at=?,last_seen_at=? WHERE id=?", (expiry, seen, session["session_id"]))
    return get_profile(session["profile_id"])


def revoke_session(raw_token: Optional[str]) -> None:
    if not raw_token:
        return
    if using_postgres():
        with postgres_connect() as db:
            db.execute("DELETE FROM sessions WHERE token_hash=%s", (_hash(raw_token),))
    else:
        with connect() as db:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (_hash(raw_token),))


def create_steam_state(profile_id: str, return_to: str) -> str:
    state = _token()
    values = (_hash(state), profile_id, return_to, _iso(_now() + timedelta(minutes=10)))
    if using_postgres():
        with postgres_connect() as db:
            db.execute("INSERT INTO steam_auth_states (state_hash,profile_id,return_to,expires_at) VALUES (%s,%s,%s,%s)", values)
    else:
        with connect() as db:
            db.execute("INSERT INTO steam_auth_states (state_hash,profile_id,return_to,expires_at) VALUES (?,?,?,?)", values)
    return state


def consume_steam_state(state: str) -> Optional[dict]:
    columns = ["profile_id", "return_to", "expires_at"]
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute("DELETE FROM steam_auth_states WHERE state_hash=%s RETURNING profile_id,return_to,expires_at", (_hash(state),)).fetchone()
    else:
        with connect() as db:
            row = db.execute("SELECT profile_id,return_to,expires_at FROM steam_auth_states WHERE state_hash=?", (_hash(state),)).fetchone()
            db.execute("DELETE FROM steam_auth_states WHERE state_hash=?", (_hash(state),))
    data = _row_dict(row, columns)
    if not data or datetime.fromisoformat(data["expires_at"]) <= _now():
        return None
    return data


def attach_steam(profile_id: str, account_id: int) -> str:
    now = _iso(_now())
    existing = None
    if using_postgres():
        with postgres_connect() as db:
            existing = db.execute("SELECT id FROM player_profiles WHERE steam_account_id=%s", (account_id,)).fetchone()
            target_id = existing[0] if existing else profile_id
            if existing and target_id != profile_id:
                db.execute("UPDATE reports SET profile_id=%s WHERE profile_id=%s", (target_id, profile_id))
                db.execute("DELETE FROM player_profiles WHERE id=%s", (profile_id,))
            else:
                db.execute("UPDATE player_profiles SET steam_account_id=%s,is_guest=FALSE,updated_at=%s WHERE id=%s", (account_id, now, profile_id))
            db.execute("UPDATE reports SET profile_id=%s WHERE account_id=%s AND profile_id IS NULL", (target_id, account_id))
    else:
        with connect() as db:
            existing = db.execute("SELECT id FROM player_profiles WHERE steam_account_id=?", (account_id,)).fetchone()
            target_id = existing[0] if existing else profile_id
            if existing and target_id != profile_id:
                db.execute("UPDATE reports SET profile_id=? WHERE profile_id=?", (target_id, profile_id))
                db.execute("DELETE FROM player_profiles WHERE id=?", (profile_id,))
            else:
                db.execute("UPDATE player_profiles SET steam_account_id=?,is_guest=0,updated_at=? WHERE id=?", (account_id, now, profile_id))
            db.execute("UPDATE reports SET profile_id=? WHERE account_id=? AND profile_id IS NULL", (target_id, account_id))
    return target_id


def create_exchange(profile_id: str) -> str:
    code = _token()
    values = (_hash(code), profile_id, _iso(_now() + timedelta(minutes=2)))
    if using_postgres():
        with postgres_connect() as db:
            db.execute("INSERT INTO auth_exchanges (code_hash,profile_id,expires_at) VALUES (%s,%s,%s)", values)
    else:
        with connect() as db:
            db.execute("INSERT INTO auth_exchanges (code_hash,profile_id,expires_at) VALUES (?,?,?)", values)
    return code


def consume_exchange(code: str) -> Optional[str]:
    columns = ["profile_id", "expires_at"]
    if using_postgres():
        with postgres_connect() as db:
            row = db.execute("DELETE FROM auth_exchanges WHERE code_hash=%s RETURNING profile_id,expires_at", (_hash(code),)).fetchone()
    else:
        with connect() as db:
            row = db.execute("SELECT profile_id,expires_at FROM auth_exchanges WHERE code_hash=?", (_hash(code),)).fetchone()
            db.execute("DELETE FROM auth_exchanges WHERE code_hash=?", (_hash(code),))
    data = _row_dict(row, columns)
    if not data or datetime.fromisoformat(data["expires_at"]) <= _now():
        return None
    session_token, _ = create_session(data["profile_id"])
    return session_token
