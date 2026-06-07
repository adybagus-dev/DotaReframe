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
    assert report.summary_note
    assert report.reflection_prompt
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


def test_generate_report_uses_gemini_wording_when_available(monkeypatch) -> None:
    metrics = calculate_player_metrics(sample_match(), 0)

    monkeypatch.setattr(
        "app.services.coach.refine_report_language",
        lambda payload: {
            "match_story": "Simple story from Gemini.",
            "main_problem": "Simple problem from Gemini.",
            "practice_drills": [
                {
                    "title": "Gemini drill",
                    "goal": "Keep it simple",
                    "how_to_practice": "Do one clear thing each game.",
                }
            ],
            "training_plan": ["Gemini step one", "Gemini step two"],
            "next_match_mission": {
                "explanation": "Simple mission explanation.",
                "check_text": "Simple mission check.",
            },
            "progress": {"message": "Simple progress text."},
            "summary_note": "Simple saved summary.",
            "reflection_prompt": "What will you do differently next game?",
        },
    )

    report = generate_report(sample_match(), metrics)

    assert report.match_story == "Simple story from Gemini."
    assert report.main_problem == "Simple problem from Gemini."
    assert report.practice_drills[0].title == "Gemini drill"
    assert report.training_plan == ["Gemini step one", "Gemini step two"]
    assert report.next_match_mission
    assert report.next_match_mission.explanation == "Simple mission explanation."
    assert report.next_match_mission.check_text == "Simple mission check."
    assert report.summary_note == "Simple saved summary."
    assert report.reflection_prompt == "What will you do differently next game?"


def test_generate_report_falls_back_when_gemini_fails(monkeypatch) -> None:
    metrics = calculate_player_metrics(sample_match(), 0)

    def boom(_payload):
        raise RuntimeError("Gemini is unavailable")

    monkeypatch.setattr("app.services.coach.refine_report_language", boom)

    report = generate_report(sample_match(), metrics)

    assert "You played" in report.match_story
    assert report.main_problem
