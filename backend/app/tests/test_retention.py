import asyncio
from pathlib import Path

from app import main
from app.schemas.report import ReportCreateRequest
from app.services import storage
from app.services.analyzer import calculate_player_metrics
from app.services.benchmarks import build_benchmark
from app.services.coach import generate_report
from app.services.identity import create_session, resolve_session, revoke_session
from app.services.opendota import OpenDotaError, fetch_match

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
    assert storage.list_reports(first["id"])[0]["summary_note"] == report.summary_note
    assert storage.get_report(report.id, first["id"])["reflection_prompt"] == report.reflection_prompt
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


def test_sqlite_schema_initializes_match_cache(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)

    storage.init_db()

    with storage.connect() as db:
        table = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='match_cache'").fetchone()
        index = db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='reports_profile_match_player_role_idx'"
        ).fetchone()
    assert table is not None
    assert index is not None


def test_match_fetch_stores_and_reuses_cache(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    calls = {"count": 0}

    async def fake_get_json(path: str) -> dict:
        calls["count"] += 1
        assert path == "/matches/8123456789"
        return sample_match()

    monkeypatch.setattr("app.services.opendota._get_json", fake_get_json)

    first = asyncio.run(fetch_match(8123456789))
    second = asyncio.run(fetch_match(8123456789))

    assert first["match_id"] == 8123456789
    assert second["match_id"] == 8123456789
    assert calls["count"] == 1


def test_match_fetch_uses_stale_cache_when_opendota_fails(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    storage.save_cached_match(8123456789, sample_match())
    with storage.connect() as db:
        db.execute("UPDATE match_cache SET fetched_at='2000-01-01T00:00:00+00:00' WHERE match_id=8123456789")

    async def fail_get_json(path: str) -> dict:
        raise OpenDotaError("OpenDota failed", 503)

    monkeypatch.setattr("app.services.opendota._get_json", fail_get_json)

    assert asyncio.run(fetch_match(8123456789))["match_id"] == 8123456789


def test_duplicate_report_returns_before_match_fetch(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, profile = create_session()
    metrics = calculate_player_metrics(sample_match(), 0, "Carry")
    report = generate_report(sample_match(), metrics)
    report.id = f"{report.id}-{profile['id'][:8]}"
    storage.save_report(report, profile["id"], metrics)

    async def fail_get_match(match_id: int) -> dict:
        raise AssertionError("OpenDota should not be called for an existing role-specific report")

    monkeypatch.setattr(main, "get_match", fail_get_match)

    payload = asyncio.run(
        main._create_personal_report(
            ReportCreateRequest(match_id=8123456789, player_slot=0, role="Carry"),
            profile,
        )
    )

    assert payload["id"] == report.id


def test_dashboard_includes_ai_coach_note(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, profile = create_session()
    metrics = calculate_player_metrics(sample_match(), 0)
    report = generate_report(sample_match(), metrics)
    report.id = f"{report.id}-{profile['id'][:8]}"
    storage.save_report(report, profile["id"], metrics)

    monkeypatch.setattr(main, "generate_dashboard_note", lambda payload: "Gemini says keep the lane safer.")

    dashboard = main.get_dashboard(profile)

    assert dashboard["coach_note"] == "Gemini says keep the lane safer."


def test_dashboard_falls_back_without_ai(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, profile = create_session()

    monkeypatch.setattr(main, "generate_dashboard_note", lambda payload: None)

    dashboard = main.get_dashboard(profile)

    assert dashboard["coach_note"].startswith("Start with one review")


def test_saved_report_detail_marks_latest_review(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, profile = create_session()
    metrics = calculate_player_metrics(sample_match(), 0)

    older = generate_report(sample_match(), {**metrics, "match_id": 7000000000})
    older.id = f"{older.id}-{profile['id'][:8]}-old"
    storage.save_report(older, profile["id"], {**metrics, "match_id": 7000000000})

    latest = generate_report(sample_match(), {**metrics, "match_id": 7000000001})
    latest.id = f"{latest.id}-{profile['id'][:8]}-new"
    storage.save_report(latest, profile["id"], {**metrics, "match_id": 7000000001})

    older_detail = main.get_personal_report(older.id, profile)
    latest_detail = main.get_personal_report(latest.id, profile)

    assert older_detail["is_latest"] is False
    assert latest_detail["is_latest"] is True


def test_dashboard_current_mission_uses_latest_review_not_latest_match(monkeypatch, tmp_path) -> None:
    use_temp_database(monkeypatch, tmp_path)
    _, profile = create_session()

    first_metrics = calculate_player_metrics(sample_match(), 0)
    first_metrics["match_id"] = 7000000002
    first_metrics["start_time"] = 2000000000
    first_metrics["deaths"] = 9
    first = generate_report(sample_match(), first_metrics)
    first.id = f"{first.id}-{profile['id'][:8]}-first"
    storage.save_report(first, profile["id"], first_metrics)

    second_metrics = calculate_player_metrics(sample_match(), 0)
    second_metrics["match_id"] = 7000000003
    second_metrics["start_time"] = 1000000000
    second_metrics["deaths"] = 2
    second_metrics["gpm"] = 320
    second = generate_report(sample_match(), second_metrics)
    second.id = f"{second.id}-{profile['id'][:8]}-second"
    storage.save_report(second, profile["id"], second_metrics)

    dashboard = main.get_dashboard(profile)

    assert dashboard["active_mission"]["title"] == second.next_match_mission.title
