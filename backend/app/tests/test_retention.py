from pathlib import Path

from app.services import storage
from app.services.analyzer import calculate_player_metrics
from app.services.benchmarks import build_benchmark
from app.services.coach import generate_report
from app.services.identity import create_session, resolve_session, revoke_session

from .test_analyzer import sample_match


def use_temp_database(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("DATABASE_MODE", raising=False)
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "retention.sqlite3")


def test_guest_session_is_hashed_and_can_be_revoked(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    token, profile = create_session()

    assert resolve_session(token)["id"] == profile["id"]
    with storage.connect() as db:
        stored = db.execute("SELECT token_hash FROM sessions").fetchone()[0]
    assert stored != token

    revoke_session(token)
    assert resolve_session(token) is None


def test_reports_are_isolated_by_profile(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, first = create_session()
    _, second = create_session()
    metrics = calculate_player_metrics(sample_match(), 0)
    report = generate_report(sample_match(), metrics)
    report.id = f"{report.id}-{first['id'][:8]}"

    storage.save_report(report, first["id"], metrics)

    assert len(storage.list_reports(first["id"])) == 1
    assert storage.list_reports(second["id"]) == []
    assert storage.get_report(report.id, second["id"]) is None


def test_feedback_can_be_changed(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, profile = create_session()
    metrics = calculate_player_metrics(sample_match(), 0)
    report = generate_report(sample_match(), metrics)
    report.id = f"{report.id}-{profile['id'][:8]}"
    storage.save_report(report, profile["id"], metrics)

    storage.save_feedback(profile["id"], report.id, False, "weak_evidence")
    storage.save_feedback(profile["id"], report.id, True, None)

    assert storage.get_feedback(profile["id"], report.id) == {"helpful": True, "reason": None}


def test_benchmark_uses_practical_target_until_cohort_is_large() -> None:
    metrics = calculate_player_metrics(sample_match(), 0)
    fallback = build_benchmark(metrics, [])
    assert fallback.source == "practical_target"

    sample = {
        "hero": metrics["hero"],
        "role": metrics["role"],
        "rank_bracket": metrics["rank_tier"] // 10,
        "duration_bucket": "30_44",
        "patch": metrics.get("patch"),
        "metrics": {
            "gpm": 500,
            "deaths": 6,
            "last_hits": 230,
            "kill_participation": 55,
            "tower_damage": 2200,
        },
    }
    cohort = build_benchmark(metrics, [sample for _ in range(30)])
    assert cohort.source == "cohort"
    assert cohort.sample_size == 30
