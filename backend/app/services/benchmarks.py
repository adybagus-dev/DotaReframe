from __future__ import annotations

from statistics import median

from app.schemas.report import BenchmarkContext, BenchmarkMetric
PRACTICAL_TARGETS = {
    "Carry": {"gpm": 560, "last_hits": 240, "tower_damage": 2500, "deaths": 6},
    "Mid": {"gpm": 500, "last_hits": 190, "tower_damage": 1800, "deaths": 6},
    "Offlane": {"gpm": 430, "last_hits": 150, "tower_damage": 1400, "deaths": 7},
    "Soft Support": {"gpm": 300, "last_hits": 65, "tower_damage": 700, "deaths": 8},
    "Hard Support": {"gpm": 260, "last_hits": 35, "tower_damage": 500, "deaths": 8},
}


def _duration_bucket(minutes: int) -> str:
    return "under_30" if minutes < 30 else "30_44" if minutes < 45 else "45_plus"


def _metric_names(role: str) -> list[tuple[str, str, str]]:
    if role in {"Soft Support", "Hard Support"}:
        return [
            ("deaths", "Deaths", "lower"),
            ("kill_participation", "Fight participation", "higher"),
            ("healing", "Hero healing", "higher"),
            ("wards_placed", "Wards placed", "higher"),
            ("camps_stacked", "Camps stacked", "higher"),
        ]
    return [
        ("gpm", "Gold per minute", "higher"),
        ("deaths", "Deaths", "lower"),
        ("last_hits", "Last hits", "higher"),
        ("kill_participation", "Fight participation", "higher"),
        ("tower_damage", "Tower damage", "higher"),
    ]


def _percentile(values: list[int], current: int, direction: str) -> int:
    favorable = sum(value <= current for value in values) if direction == "higher" else sum(value >= current for value in values)
    return round(favorable / len(values) * 100)


def build_benchmark(metrics: dict, samples: list[dict]) -> BenchmarkContext:
    role = metrics["role"]
    rank_bracket = metrics.get("rank_tier")
    rank_bracket = rank_bracket // 10 if rank_bracket else None
    duration_bucket = _duration_bucket(metrics["duration_minutes"])
    patch = metrics.get("patch")

    cohorts = [
        (
            "Same hero, role, rank, duration, and patch",
            30,
            lambda item: item["hero"] == metrics["hero"]
            and item["role"] == role
            and item["rank_bracket"] == rank_bracket
            and item["duration_bucket"] == duration_bucket
            and item["patch"] == patch,
        ),
        (
            "Same hero, role, rank, and duration",
            30,
            lambda item: item["hero"] == metrics["hero"]
            and item["role"] == role
            and item["rank_bracket"] == rank_bracket
            and item["duration_bucket"] == duration_bucket,
        ),
        (
            "Same role, rank, and duration",
            50,
            lambda item: item["role"] == role
            and item["rank_bracket"] == rank_bracket
            and item["duration_bucket"] == duration_bucket,
        ),
    ]
    for label, minimum, predicate in cohorts:
        cohort = [item for item in samples if predicate(item)]
        if len(cohort) >= minimum:
            result = []
            for name, metric_label, direction in _metric_names(role):
                values = [int(item["metrics"].get(name) or 0) for item in cohort]
                current = int(metrics.get(name) or 0)
                result.append(
                    BenchmarkMetric(
                        metric=name,
                        label=metric_label,
                        user_value=current,
                        comparison_value=round(median(values)),
                        percentile=_percentile(values, current, direction),
                        direction=direction,
                    )
                )
            return BenchmarkContext(source="cohort", label=label, sample_size=len(cohort), metrics=result)

    profile = PRACTICAL_TARGETS.get(role, PRACTICAL_TARGETS["Offlane"])
    practical = {
        "gpm": profile["gpm"],
        "deaths": profile["deaths"] - 1,
        "last_hits": profile["last_hits"],
        "kill_participation": 55,
        "tower_damage": profile["tower_damage"],
        "healing": 1000,
        "wards_placed": 10,
        "camps_stacked": 3,
    }
    result = [
        BenchmarkMetric(
            metric=name,
            label=label,
            user_value=int(metrics.get(name) or 0),
            comparison_value=int(practical[name]),
            direction=direction,
        )
        for name, label, direction in _metric_names(role)
    ]
    return BenchmarkContext(
        source="practical_target",
        label=f"Practical {role} target",
        sample_size=0,
        metrics=result,
    )
