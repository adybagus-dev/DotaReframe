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
