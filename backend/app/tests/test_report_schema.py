from app.services.analyzer import calculate_player_metrics
from app.services.coach import generate_report

from .test_analyzer import sample_match


def test_generate_report_contains_required_sections() -> None:
    metrics = calculate_player_metrics(sample_match(), 0)
    report = generate_report(sample_match(), metrics)

    assert report.id == "report-8123456789-0-carry"
    assert report.main_problem
    assert report.mistakes
    assert report.mistakes[0].evidence
    assert report.training_plan
    assert report.limitations
    assert report.next_match_mission
    assert report.comparison_context
    assert report.timeline[0].title == "Bought Phase Boots"


def test_generate_report_uses_role_specific_expectations() -> None:
    metrics = calculate_player_metrics(sample_match(), 0, "Hard Support")
    report = generate_report(sample_match(), metrics)

    assert report.role == "Hard Support"
    assert report.performance_snapshot["farming"] == "Good"
    assert any("Hard Support" in item for item in report.decision_rules)


def test_generate_report_compares_previous_mission() -> None:
    metrics = calculate_player_metrics(sample_match(), 0)
    previous = generate_report(sample_match(), {**metrics, "match_id": 7000000000})
    previous_payload = previous.model_dump()
    previous_payload["next_match_mission"] = {
        "title": "Finish with 8 deaths or fewer",
        "metric": "deaths",
        "target": 8,
        "direction": "at_most",
        "explanation": "Stay alive.",
        "check_text": "Check deaths.",
    }

    report = generate_report(sample_match(), metrics, [previous_payload])

    assert report.progress
    assert report.progress.completed is True
