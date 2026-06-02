from app.services.analyzer import calculate_player_metrics
from app.services.coach import generate_report

from .test_analyzer import sample_match


def test_generate_report_contains_required_sections() -> None:
    metrics = calculate_player_metrics(sample_match(), 0)
    report = generate_report(sample_match(), metrics)

    assert report.id == "report-8123456789-0"
    assert report.main_problem
    assert report.mistakes
    assert report.mistakes[0].evidence
    assert report.training_plan
    assert report.limitations
