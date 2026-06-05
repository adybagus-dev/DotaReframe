from datetime import date

from app.schemas.report import CoachingReport, Mistake, PracticeDrill, ReportSummary, TimingNote


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
            "This review is based on match stats and may not fully understand positioning, voice calls, or team strategy."
        ],
    )


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
