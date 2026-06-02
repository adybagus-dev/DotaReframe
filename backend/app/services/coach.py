from datetime import date

from app.schemas.report import CoachingReport, Mistake, PracticeDrill, ReportSummary, TimingNote


def generate_report(match: dict, metrics: dict) -> CoachingReport:
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
    return CoachingReport(
        id=f"report-{metrics['match_id']}-{metrics['player_slot']}",
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
        training_plan=[
            "Game 1: Play around one clear timing. Do not join optional fights before your first important item.",
            "Game 2: After every won fight, immediately call one objective: tower, Roshan, or enemy jungle.",
            "Game 3: Before walking into a dark area, say what enemy heroes can kill you there.",
        ],
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
            "This review is based on match stats and may not fully understand positioning, voice calls, or team strategy."
        ],
    )


def _match_story(metrics: dict) -> str:
    result_noun = "win" if metrics["result"] == "Won" else "loss"
    role_phrase = f" as {metrics['role']}" if metrics["role"] != "Unknown Role" else ""
    return (
        f"You played {metrics['hero']}{role_phrase} and finished with {metrics['kda']} in a "
        f"{metrics['duration_minutes']}-minute {result_noun}. Your fight impact was visible "
        f"({metrics['hero_damage']} hero damage), but the review points to two practical leaks: "
        f"{metrics['deaths']} deaths and only {metrics['tower_damage']} tower damage. The next step is not "
        "to play scared. The next step is to choose fights that protect your timing or turn into objectives."
    )


def _snapshot(metrics: dict) -> dict[str, str]:
    return {
        "farming": "Good" if metrics["gpm"] >= 550 or metrics["last_hits"] >= 260 else "Needs Work",
        "fighting": "Good" if metrics["kill_participation"] >= 55 or metrics["hero_damage"] >= 18000 else "Okay",
        "survival": "Needs Work" if metrics["deaths"] >= 7 else "Good",
        "objectives": "Low Impact" if metrics["tower_damage"] < 2000 else "Good",
    }


def _timing_notes(metrics: dict) -> list[TimingNote]:
    early_action = (
        "Keep your lane and nearby camps connected. If a fight starts far from your farm, skip it unless your tower is dying."
        if metrics["gpm"] < 560
        else "Your farm pace is stable, so keep using lane pressure to force better fights."
    )
    mid_action = (
        "When you win a fight, ping the closest tower or enemy jungle camp before farming your own side again."
        if metrics["tower_damage"] < 2500
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
            what_to_notice=f"Your lane should build toward stable farm. Current final GPM: {metrics['gpm']}.",
            do_next_game=early_action,
        ),
        TimingNote(
            phase="10-25 min",
            what_to_notice=f"This is where optional fights can slow your item timing. Deaths this game: {metrics['deaths']}.",
            do_next_game="Join fights that defend a tower, secure a rune/objective, or happen next to your farming path.",
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

    if metrics["deaths"] >= 7:
        mistakes.append(
            Mistake(
                title="You died in unsafe areas",
                what_happened=(
                    "You gave away too many deaths. The important part is not the number alone; it is that each death "
                    "stops your farming, delays your next fight, and gives the enemy time to take space."
                ),
                evidence=[f"Deaths: {metrics['deaths']}", f"KDA: {metrics['kda']}"],
                why_it_matters="Every death removes you from the map and gives the enemy time to take space.",
                try_next_game=(
                    "Before walking into a dark area, ask: who can kill me, and where were they last seen? "
                    "If you cannot answer, farm a safer camp or wait for vision."
                ),
            )
        )

    if metrics["gpm"] < 520:
        mistakes.append(
            Mistake(
                title="Your farming pace was a bit slow",
                what_happened=(
                    "Your gold growth was not high enough for the kind of control your role needs. "
                    "This usually happens when you leave your farming pattern for fights that do not protect towers or win objectives."
                ),
                evidence=[f"GPM: {metrics['gpm']}", f"Last hits: {metrics['last_hits']}"],
                why_it_matters="Core heroes need steady gold before they can take strong fights.",
                try_next_game=(
                    "Use a simple loop: push the safe lane wave, take the closest jungle camp, then check the minimap. "
                    "Only break the loop for a tower defense, Roshan fight, or a fight beside your team."
                ),
            )
        )

    if metrics["tower_damage"] < 2000:
        mistakes.append(
            Mistake(
                title="Kills did not become towers",
                what_happened=(
                    "You had fight impact, but your building damage stayed low. That means some won moments became only kills, "
                    "not map control."
                ),
                evidence=[f"Tower damage: {metrics['tower_damage']}", f"Hero damage: {metrics['hero_damage']}"],
                why_it_matters="Kills matter more when they lead to towers, Roshan, or enemy jungle control.",
                try_next_game=(
                    "After every won fight, look at the closest lane first. If the wave is near a tower, hit the tower. "
                    "If not, take enemy jungle camps or set up Roshan."
                ),
            )
        )

    if not mistakes:
        mistakes.append(
            Mistake(
                title="Focus on one clear next step",
                what_happened="Your basic stats look stable, so the best next step is cleaner objective conversion.",
                evidence=[f"KDA: {metrics['kda']}", f"Tower damage: {metrics['tower_damage']}"],
                why_it_matters="Good games become easier to win when your team turns advantages into map control.",
                try_next_game="After won fights, call one simple objective: tower, Roshan, or enemy jungle.",
            )
        )

    return mistakes[:3]


def _decision_rules(metrics: dict) -> list[str]:
    return [
        "Join a fight before your item timing only if it protects your tower, secures Roshan, or happens beside your farming path.",
        "If two or more enemy heroes are missing and your team has no vision, do not walk into the next dark area first.",
        "After a won fight, choose one objective within 5 seconds: tower, Roshan, enemy jungle, or lane shove.",
        f"If your deaths reach {max(3, metrics['deaths'] - 2)} before 25 minutes next game, slow down and farm closer to vision.",
    ]


def _next_game_checklist(metrics: dict) -> list[str]:
    target_deaths = max(3, metrics["deaths"] - 2)
    target_tower_damage = max(2000, metrics["tower_damage"] + 800)
    target_gpm = max(520, metrics["gpm"] + 30)
    return [
        f"Keep deaths at {target_deaths} or lower.",
        f"Reach at least {target_gpm} GPM if you play a farming core.",
        f"Deal at least {target_tower_damage} tower damage or clearly help take two objectives.",
        "Skip at least one fight that is far from your farm and does not defend a tower.",
        "After each death, write one sentence: what made that area unsafe?",
    ]


def _practice_drills(metrics: dict) -> list[PracticeDrill]:
    return [
        PracticeDrill(
            title="Safe farm loop",
            goal="Build a habit of farming without walking into dead areas.",
            how_to_practice=(
                "For 10 minutes, repeat: push a safe wave, take one nearby camp, check minimap, then decide. "
                "Do not cross the river unless enemy heroes show or your team is with you."
            ),
        ),
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
