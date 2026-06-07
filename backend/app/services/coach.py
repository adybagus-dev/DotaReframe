from __future__ import annotations

from datetime import date

from app.schemas.report import (
    CoachingReport,
    ComparisonContext,
    Mistake,
    NextMatchMission,
    PracticeDrill,
    ProgressComparison,
    ReportSummary,
    TimelineEvent,
    TimingNote,
)
from app.services.benchmarks import build_benchmark
from app.services.gemini import refine_report_language


ROLE_PROFILES = {
    "Carry": {
        "gpm": 560,
        "last_hits": 240,
        "tower_damage": 2500,
        "deaths": 6,
        "farm_label": "carry farm pace",
        "objective_label": "building pressure",
    },
    "Mid": {
        "gpm": 500,
        "last_hits": 190,
        "tower_damage": 1800,
        "deaths": 6,
        "farm_label": "mid-game tempo",
        "objective_label": "tower or rune pressure",
    },
    "Offlane": {
        "gpm": 430,
        "last_hits": 150,
        "tower_damage": 1400,
        "deaths": 7,
        "farm_label": "offlane item pace",
        "objective_label": "space and tower pressure",
    },
    "Soft Support": {
        "gpm": 300,
        "last_hits": 65,
        "tower_damage": 700,
        "deaths": 8,
        "farm_label": "support resource pace",
        "objective_label": "fight setup and tower help",
    },
    "Hard Support": {
        "gpm": 260,
        "last_hits": 35,
        "tower_damage": 500,
        "deaths": 8,
        "farm_label": "hard support resource pace",
        "objective_label": "vision, saves, and tower help",
    },
}


def _profile(metrics: dict) -> dict:
    return ROLE_PROFILES.get(metrics["role"], ROLE_PROFILES["Offlane"])


def _role_slug(role: str) -> str:
    return role.lower().replace(" ", "-")


def generate_report(
    match: dict,
    metrics: dict,
    previous_reports: list[dict] | None = None,
    benchmark_samples: list[dict] | None = None,
) -> CoachingReport:
    mistakes = _mistakes(metrics)
    main = mistakes[0]
    summary = ReportSummary(
        duration_minutes=metrics["duration_minutes"],
        kda=metrics["kda"],
        gpm=metrics["gpm"],
        xpm=metrics["xpm"],
        last_hits=metrics["last_hits"],
        denies=metrics["denies"],
        hero_damage=metrics["hero_damage"],
        tower_damage=metrics["tower_damage"],
        deaths=metrics["deaths"],
    )
    report = CoachingReport(
        id=f"report-{metrics['match_id']}-{metrics['player_slot']}-{_role_slug(metrics['role'])}",
        match_id=metrics["match_id"],
        player_slot=metrics["player_slot"],
        hero=metrics["hero"],
        role=metrics["role"],
        result=metrics["result"],
        created_at=date.today().isoformat(),
        summary=summary,
        match_story=_match_story(metrics),
        main_problem=main.title,
        main_evidence=main.evidence,
        performance_snapshot=_snapshot(metrics),
        timing_notes=_timing_notes(metrics),
        mistakes=mistakes,
        decision_rules=_decision_rules(metrics),
        next_game_checklist=_next_game_checklist(metrics),
        practice_drills=_practice_drills(metrics),
        strengths=_strengths(metrics),
        training_plan=_training_plan(metrics),
        match_evidence=[
            f"Duration: {metrics['duration_minutes']} minutes",
            f"KDA: {metrics['kda']}",
            f"GPM: {metrics['gpm']}",
            f"XPM: {metrics['xpm']}",
            f"Last hits: {metrics['last_hits']}",
            f"Tower damage: {metrics['tower_damage']}",
        ],
        confidence="medium",
        limitations=[
            "This review is based on available OpenDota data and may not fully understand positioning, voice calls, or team strategy."
        ],
        account_id=metrics.get("account_id"),
        comparison_context=_comparison_context(metrics),
        benchmark_context=build_benchmark(metrics, benchmark_samples or []),
        next_match_mission=_next_match_mission(metrics),
        timeline=_timeline(metrics),
        progress=_progress(metrics, previous_reports or []),
        summary_note=_summary_note(metrics, main),
        reflection_prompt=_reflection_prompt(metrics, main),
    )
    return _refine_with_gemini(report)


def _refine_with_gemini(report: CoachingReport) -> CoachingReport:
    try:
        refined = refine_report_language(
            {
                "role": report.role,
                "hero": report.hero,
                "result": report.result,
                "summary": report.summary.model_dump(),
                "main_problem": report.main_problem,
                "match_story": report.match_story,
                "next_match_mission": report.next_match_mission.model_dump() if report.next_match_mission else None,
                "progress": report.progress.model_dump() if report.progress else None,
                "practice_drills": [drill.model_dump() for drill in report.practice_drills],
                "training_plan": list(report.training_plan),
                "summary_note": report.summary_note,
                "reflection_prompt": report.reflection_prompt,
            }
        )
    except Exception:
        return report

    if not refined:
        return report

    if isinstance(refined.get("match_story"), str) and refined["match_story"].strip():
        report.match_story = refined["match_story"].strip()
    if isinstance(refined.get("main_problem"), str) and refined["main_problem"].strip():
        report.main_problem = refined["main_problem"].strip()

    drills = refined.get("practice_drills")
    if isinstance(drills, list) and drills:
        updated_drills: list[PracticeDrill] = []
        for index, original in enumerate(report.practice_drills):
            updated = drills[index] if index < len(drills) else None
            if isinstance(updated, dict):
                updated_drills.append(
                    PracticeDrill(
                        title=str(updated.get("title") or original.title).strip(),
                        goal=str(updated.get("goal") or original.goal).strip(),
                        how_to_practice=str(updated.get("how_to_practice") or original.how_to_practice).strip(),
                    )
                )
            else:
                updated_drills.append(original)
        report.practice_drills = updated_drills

    plan = refined.get("training_plan")
    if isinstance(plan, list) and plan:
        refined_plan = [str(item).strip() for item in plan if str(item).strip()]
        if refined_plan:
            report.training_plan = refined_plan[: len(report.training_plan)]

    next_mission = refined.get("next_match_mission")
    if report.next_match_mission and isinstance(next_mission, dict):
        if isinstance(next_mission.get("explanation"), str) and next_mission["explanation"].strip():
            report.next_match_mission.explanation = next_mission["explanation"].strip()
        if isinstance(next_mission.get("check_text"), str) and next_mission["check_text"].strip():
            report.next_match_mission.check_text = next_mission["check_text"].strip()

    progress = refined.get("progress")
    if report.progress and isinstance(progress, dict):
        if isinstance(progress.get("message"), str) and progress["message"].strip():
            report.progress.message = progress["message"].strip()

    if isinstance(refined.get("summary_note"), str) and refined["summary_note"].strip():
        report.summary_note = refined["summary_note"].strip()
    if isinstance(refined.get("reflection_prompt"), str) and refined["reflection_prompt"].strip():
        report.reflection_prompt = refined["reflection_prompt"].strip()

    return report


def _summary_note(metrics: dict, main: Mistake) -> str:
    return (
        f"{metrics['hero']} {metrics['role']}: {main.title.lower()} is the next habit to clean up."
    )


def _reflection_prompt(metrics: dict, main: Mistake) -> str:
    return (
        f"Before your next {metrics['role']} game, what one decision will help avoid this: {main.title.lower()}?"
    )


def _duration_bucket(minutes: int) -> str:
    if minutes < 30:
        return "short match (under 30 minutes)"
    if minutes < 45:
        return "standard match (30-44 minutes)"
    return "long match (45+ minutes)"


def _rank_label(rank_tier: int | None) -> str | None:
    if not rank_tier:
        return None
    medals = {
        1: "Herald",
        2: "Guardian",
        3: "Crusader",
        4: "Archon",
        5: "Legend",
        6: "Ancient",
        7: "Divine",
        8: "Immortal",
    }
    medal = medals.get(rank_tier // 10)
    return f"{medal} bracket" if medal else f"Rank tier {rank_tier}"


def _comparison_context(metrics: dict) -> ComparisonContext:
    profile = _profile(metrics)
    return ComparisonContext(
        role=metrics["role"],
        hero=metrics["hero"],
        duration_bucket=_duration_bucket(metrics["duration_minutes"]),
        rank_label=_rank_label(metrics.get("rank_tier")),
        patch=f"Patch ID {metrics['patch']}" if metrics.get("patch") is not None else None,
        baseline=(
            f"Compared with a practical {metrics['role']} baseline: about {profile['gpm']} GPM, "
            f"{profile['tower_damage']} tower damage, and fewer than {profile['deaths']} deaths."
        ),
    )


def _next_match_mission(metrics: dict) -> NextMatchMission:
    profile = _profile(metrics)
    if metrics["deaths"] >= profile["deaths"]:
        target = max(3, min(profile["deaths"] - 1, metrics["deaths"] - 2))
        return NextMatchMission(
            title=f"Finish with {target} deaths or fewer",
            metric="deaths",
            target=target,
            direction="at_most",
            explanation="Staying alive protects your item timing, map pressure, and ability to join the next objective.",
            check_text=f"After the match, check whether deaths are {target} or lower.",
        )
    if metrics["gpm"] < profile["gpm"]:
        target = min(profile["gpm"], metrics["gpm"] + 40)
        return NextMatchMission(
            title=f"Reach at least {target} GPM",
            metric="gpm",
            target=target,
            direction="at_least",
            explanation=f"This is a small, role-aware step toward a healthier {metrics['role']} resource pace.",
            check_text=f"After the match, check whether GPM reached {target}.",
        )
    if metrics.get("is_parsed"):
        target = max(profile["tower_damage"], metrics["tower_damage"] + 300)
        return NextMatchMission(
            title=f"Create {target}+ tower damage",
            metric="tower_damage",
            target=target,
            direction="at_least",
            explanation="This turns useful fights into map control instead of ending with kills alone.",
            check_text=f"After the match, check whether tower damage reached {target}.",
        )
    target = max(3, metrics["deaths"])
    return NextMatchMission(
        title=f"Keep deaths at {target} or fewer again",
        metric="deaths",
        target=target,
        direction="at_most",
        explanation="OpenDota has basic data for this match, so survival is the clearest measurable habit to repeat.",
        check_text=f"After the match, check whether deaths are {target} or lower.",
    )


def _timeline(metrics: dict) -> list[TimelineEvent]:
    if not metrics.get("is_parsed"):
        return []
    events: list[TimelineEvent] = []
    for purchase in metrics.get("purchase_log", []):
        time = int(purchase.get("time") or 0)
        if time < 0:
            continue
        item = str(purchase.get("key") or "item").replace("_", " ").title()
        events.append(
            TimelineEvent(
                minute=time // 60,
                category="item",
                title=f"Bought {item}",
                detail="Item timing from parsed match data.",
                tone="info",
            )
        )

    player_index = metrics["player_slot"] if metrics["player_slot"] < 128 else metrics["player_slot"] - 128
    for fight in metrics.get("teamfights", []):
        players = fight.get("players") or []
        if player_index >= len(players):
            continue
        player_fight = players[player_index] or {}
        deaths = int(player_fight.get("deaths") or 0)
        if deaths:
            events.append(
                TimelineEvent(
                    minute=max(0, int(fight.get("start") or 0) // 60),
                    category="death",
                    title="Died during a teamfight",
                    detail=f"OpenDota recorded {deaths} death in this fight window.",
                    tone="risk",
                )
            )

    for objective in metrics.get("objectives", []):
        objective_type = str(objective.get("type") or "")
        if objective_type not in {"CHAT_MESSAGE_TOWER_KILL", "CHAT_MESSAGE_ROSHAN_KILL"}:
            continue
        label = "Tower taken" if "TOWER" in objective_type else "Roshan taken"
        events.append(
            TimelineEvent(
                minute=max(0, int(objective.get("time") or 0) // 60),
                category="objective",
                title=label,
                detail="Objective event from parsed match data.",
                tone="good",
            )
        )

    events.sort(key=lambda event: event.minute)
    return events[:12]


def _metric_value(report_or_metrics: dict, metric: str) -> int:
    summary = report_or_metrics.get("summary") or report_or_metrics
    if metric == "kill_participation":
        return int(report_or_metrics.get("kill_participation") or 0)
    return int(summary.get(metric) or 0)


def _progress(metrics: dict, previous_reports: list[dict]) -> ProgressComparison | None:
    for previous in previous_reports:
        if previous.get("match_id") == metrics["match_id"]:
            continue
        if previous.get("role") != metrics["role"]:
            continue
        if metrics.get("account_id") and previous.get("account_id") not in {None, metrics["account_id"]}:
            continue
        mission = previous.get("next_match_mission")
        if not mission:
            continue
        metric = mission.get("metric")
        if metric == "tower_damage" and not metrics.get("is_parsed"):
            continue
        target = int(mission.get("target") or 0)
        current_value = _metric_value(metrics, metric)
        previous_value = _metric_value(previous, metric)
        completed = current_value <= target if mission.get("direction") == "at_most" else current_value >= target
        return ProgressComparison(
            previous_report_id=previous["id"],
            previous_match_id=int(previous["match_id"]),
            mission_title=mission["title"],
            completed=completed,
            previous_value=previous_value,
            current_value=current_value,
            message=(
                f"Mission complete. Your {metric.replace('_', ' ')} moved from {previous_value} to {current_value}."
                if completed
                else f"Still in progress. Your {metric.replace('_', ' ')} moved from {previous_value} to {current_value}; target: {target}."
            ),
        )
    return None


def _match_story(metrics: dict) -> str:
    result_noun = "win" if metrics["result"] == "Won" else "loss"
    role_phrase = f" as {metrics['role']}" if metrics["role"] != "Unknown Role" else ""
    profile = _profile(metrics)
    return (
        f"You played {metrics['hero']}{role_phrase} and finished with {metrics['kda']} in a "
        f"{metrics['duration_minutes']}-minute {result_noun}. I am judging the stats against {metrics['role']} expectations, "
        f"so {metrics['gpm']} GPM is compared to about {profile['gpm']} GPM, not to a carry if you picked support. "
        f"The useful clues are {metrics['deaths']} deaths, {metrics['hero_damage']} hero damage, and "
        f"{metrics['tower_damage']} tower damage. The next step is to make your role's job clearer next game."
    )


def _snapshot(metrics: dict) -> dict[str, str]:
    profile = _profile(metrics)
    return {
        "farming": "Good" if metrics["gpm"] >= profile["gpm"] or metrics["last_hits"] >= profile["last_hits"] else "Needs Work",
        "fighting": "Good" if metrics["kill_participation"] >= 55 or metrics["hero_damage"] >= 18000 else "Okay",
        "survival": "Needs Work" if metrics["deaths"] >= profile["deaths"] else "Good",
        "objectives": "Low Impact" if metrics["tower_damage"] < profile["tower_damage"] else "Good",
    }


def _timing_notes(metrics: dict) -> list[TimingNote]:
    profile = _profile(metrics)
    is_support = metrics["role"] in {"Soft Support", "Hard Support"}
    early_action = (
        "Use pulls, lane pressure, and safe small camps to keep your resources moving without stealing your core's farm."
        if is_support and metrics["gpm"] < profile["gpm"]
        else "Keep your lane and nearby camps connected. If a fight starts far from your farm, skip it unless your tower is dying."
        if metrics["gpm"] < profile["gpm"]
        else "Your resource pace is stable for this role, so keep using lane pressure to force better fights."
    )
    mid_action = (
        "When you win a fight, ping the closest tower or enemy jungle camp before farming your own side again."
        if metrics["tower_damage"] < profile["tower_damage"]
        else "Keep converting won fights into building damage. That is already one of your better habits."
    )
    late_action = (
        "Do not enter fog first. Let a tankier hero or vision spell check the area before you commit."
        if metrics["deaths"] >= 7
        else "Keep your buyback and objective timing in mind before taking the next fight."
    )
    return [
        TimingNote(
            phase="0-10 min",
            what_to_notice=(
                f"Your lane should build toward your {metrics['role']} job. Current final GPM: {metrics['gpm']} "
                f"against a rough {metrics['role']} target of {profile['gpm']}."
            ),
            do_next_game=early_action,
        ),
        TimingNote(
            phase="10-25 min",
            what_to_notice=f"This is where optional fights can slow your role timing. Deaths this game: {metrics['deaths']}.",
            do_next_game="Join fights that defend a tower, secure a rune/objective, protect your core, or happen next to your team's path.",
        ),
        TimingNote(
            phase="After won fights",
            what_to_notice=f"Tower damage ended at {metrics['tower_damage']}. This shows how much pressure became buildings.",
            do_next_game=mid_action,
        ),
        TimingNote(
            phase="Late game",
            what_to_notice="One unsafe death can decide the map when death timers are long.",
            do_next_game=late_action,
        ),
    ]


def _mistakes(metrics: dict) -> list[Mistake]:
    mistakes: list[Mistake] = []
    profile = _profile(metrics)
    is_support = metrics["role"] in {"Soft Support", "Hard Support"}

    if metrics["deaths"] >= profile["deaths"]:
        parsed = bool(metrics.get("is_parsed"))
        mistakes.append(
            Mistake(
                title="You died in unsafe areas" if parsed else "Your deaths may come from unsafe map movement",
                what_happened=(
                    "The final statistics show a high death count. Without parsed event timing, the report cannot confirm each position, "
                    "but repeated deaths often come from entering areas without enough information."
                ),
                evidence=[f"Deaths: {metrics['deaths']}", f"KDA: {metrics['kda']}"],
                confidence="high" if parsed else "low",
                evidence_source="parsed_events" if parsed else "final_stats",
                why_it_matters="Every death removes you from the map and gives the enemy time to take space.",
                try_next_game=(
                    f"As {metrics['role']}, before walking into a dark area, ask: who can kill me, and where were they last seen? "
                    "If you cannot answer, farm a safer camp or wait for vision."
                ),
            )
        )

    if metrics["gpm"] < profile["gpm"]:
        if is_support:
            what_happened = (
                "Your gold was low even for a support role. This is not about matching a carry's GPM. "
                "It usually means you may have missed safe pulls, bounty/rune movement, stacked camps, or clean lane waves after fights."
            )
            why_it_matters = "Support heroes still need enough gold for wards, saves, mobility, and survival items."
            try_next = (
                "After each lane action, look for one safe resource: pull, stack, bounty rune, wisdom rune, or a wave your core is not taking."
            )
        else:
            what_happened = (
                "Your gold growth was low for this core role. This usually happens when you leave your farming pattern "
                "for fights that do not protect towers or win objectives."
            )
            why_it_matters = "Core heroes need steady gold before they can take strong fights."
            try_next = (
                "Use a simple loop: push the safe lane wave, take the closest jungle camp, then check the minimap. "
                "Only break the loop for a tower defense, Roshan fight, or a fight beside your team."
            )
        mistakes.append(
            Mistake(
                title=f"Your {profile['farm_label']} was low",
                what_happened=what_happened,
                evidence=[f"Role: {metrics['role']}", f"GPM: {metrics['gpm']} / role target: {profile['gpm']}"],
                confidence="medium",
                evidence_source="practical_target",
                why_it_matters=why_it_matters,
                try_next_game=try_next,
            )
        )

    if metrics["tower_damage"] < profile["tower_damage"]:
        support_context = (
            "For support, this does not mean you must hit towers like a carry. It means your fight wins should help the team reach towers, "
            "place vision around them, or protect the hero hitting them."
            if is_support
            else "That means some won moments became only kills, not map control."
        )
        mistakes.append(
            Mistake(
                title="Kills did not become towers",
                what_happened=(
                    f"You had fight impact, but your {profile['objective_label']} stayed low. {support_context}"
                ),
                evidence=[
                    f"Role: {metrics['role']}",
                    f"Tower damage: {metrics['tower_damage']} / role target: {profile['tower_damage']}",
                    f"Hero damage: {metrics['hero_damage']}",
                ],
                confidence="medium",
                evidence_source="practical_target",
                why_it_matters="Kills matter more when they lead to towers, Roshan, or enemy jungle control.",
                try_next_game=(
                    "After every won fight, look at the closest lane first. If the wave is near a tower, help your team hit, ward, or guard it. "
                    "If not, take enemy jungle space or set up Roshan."
                ),
            )
        )

    if not mistakes:
        mistakes.append(
            Mistake(
                title="Focus on one clear next step",
                what_happened="Your basic stats look stable, so the best next step is cleaner objective conversion.",
                evidence=[f"KDA: {metrics['kda']}", f"Tower damage: {metrics['tower_damage']}"],
                confidence="low",
                evidence_source="final_stats",
                why_it_matters="Good games become easier to win when your team turns advantages into map control.",
                try_next_game="After won fights, call one simple objective: tower, Roshan, or enemy jungle.",
            )
        )

    return mistakes[:3]


def _decision_rules(metrics: dict) -> list[str]:
    profile = _profile(metrics)
    return [
        f"Judge your stats as {metrics['role']}: about {profile['gpm']} GPM is a useful resource target, not a universal carry number.",
        "Join a fight before your timing only if it protects your tower, secures Roshan, saves your core, or happens beside your team's path.",
        "If two or more enemy heroes are missing and your team has no vision, do not walk into the next dark area first.",
        "After a won fight, choose one objective within 5 seconds: tower, Roshan, enemy jungle, or lane shove.",
        f"If your deaths reach {max(3, min(profile['deaths'], metrics['deaths'] - 2))} before 25 minutes next game, slow down and play closer to vision.",
    ]


def _next_game_checklist(metrics: dict) -> list[str]:
    profile = _profile(metrics)
    is_support = metrics["role"] in {"Soft Support", "Hard Support"}
    target_deaths = max(3, min(profile["deaths"], metrics["deaths"] - 2))
    target_tower_damage = profile["tower_damage"] if is_support else max(profile["tower_damage"], metrics["tower_damage"] + 400)
    target_gpm = profile["gpm"] if is_support else max(profile["gpm"], metrics["gpm"] + 20)

    resource_item = (
        f"Keep support resources healthy: around {target_gpm}+ GPM from pulls, stacks, runes, and unused waves, without stealing core farm."
        if is_support
        else f"Reach at least {target_gpm} GPM for this role."
    )
    objective_item = (
        "Help take at least two objectives through vision, saves, tower hits, or guarding the hero hitting buildings."
        if is_support
        else f"Create at least {target_tower_damage} tower damage or clearly help take two objectives."
    )
    return [
        f"Play the next match as {metrics['role']} and keep deaths at {target_deaths} or lower.",
        resource_item,
        objective_item,
        "Skip at least one fight that is far from your job and does not defend a tower, rune, Roshan, or core hero.",
        "After each death, write one sentence: what made that area unsafe?",
    ]


def _training_plan(metrics: dict) -> list[str]:
    if metrics["role"] in {"Soft Support", "Hard Support"}:
        return [
            "Game 1: Before leaving lane, choose one support job: pull, stack, secure rune, protect core, or place vision.",
            "Game 2: After every won fight, help the team choose one objective: tower, Roshan, enemy jungle vision, or lane shove.",
            "Game 3: Before walking into fog, say which enemy hero can kill you and whether your team can trade for it.",
        ]
    return [
        "Game 1: Play around one clear timing. Do not join optional fights before your first important item.",
        "Game 2: After every won fight, immediately call one objective: tower, Roshan, or enemy jungle.",
        "Game 3: Before walking into a dark area, say what enemy heroes can kill you there.",
    ]


def _practice_drills(metrics: dict) -> list[PracticeDrill]:
    is_support = metrics["role"] in {"Soft Support", "Hard Support"}
    first_drill = (
        PracticeDrill(
            title="Support resource loop",
            goal="Get useful gold and XP without taking your core's main farm.",
            how_to_practice=(
                "For 10 minutes, repeat: check if your core is safe, pull or stack if the lane allows it, secure rune timing, "
                "then take only waves or camps your core is not using."
            ),
        )
        if is_support
        else PracticeDrill(
            title="Safe farm loop",
            goal="Build a habit of farming without walking into dead areas.",
            how_to_practice=(
                "For 10 minutes, repeat: push a safe wave, take one nearby camp, check minimap, then decide. "
                "Do not cross the river unless enemy heroes show or your team is with you."
            ),
        )
    )
    return [
        first_drill,
        PracticeDrill(
            title="Fight-to-objective check",
            goal="Turn kills into something that helps win.",
            how_to_practice=(
                "After every won fight, say out loud: tower, Roshan, enemy jungle, or reset. Pick one before farming your own jungle."
            ),
        ),
        PracticeDrill(
            title="Death review",
            goal="Reduce repeat deaths in the same unsafe areas.",
            how_to_practice=(
                f"Your current death count was {metrics['deaths']}. Next game, pause after each death and name the missing information: "
                "no ward, missing enemy hero, no teammate nearby, or overstay."
            ),
        ),
    ]


def _strengths(metrics: dict) -> list[str]:
    strengths = []
    if metrics["kill_participation"] >= 55:
        strengths.append("Good teamfight participation.")
    if metrics["last_hits"] >= 240:
        strengths.append("Solid last-hit count by the end of the match.")
    if metrics["hero_damage"] >= 18000:
        strengths.append("You contributed meaningful hero damage in fights.")
    return strengths or ["You had enough useful stats to create a clear practice plan."]
