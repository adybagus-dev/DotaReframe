import os
from pathlib import Path

from app.env import load_environment
from app.services.storage import database_backend, using_postgres


def test_local_database_defaults_to_sqlite_even_with_database_url(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_MODE", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/postgres")

    assert database_backend() == "sqlite"
    assert using_postgres() is False


def test_postgres_requires_explicit_database_mode(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_MODE", "postgres")

    assert database_backend() == "postgres"
    assert using_postgres() is True


def test_environment_loader_reads_local_env_files(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path
    (root / "backend").mkdir()
    (root / ".env.local").write_text("GEMINI_MODEL=from-file\nGEMINI_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "already-set")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    load_environment(root)

    assert os.environ["GEMINI_API_KEY"] == "already-set"
    assert os.environ["GEMINI_MODEL"] == "from-file"
