from __future__ import annotations

from app.schemas.report import ItemTimingCheckpoint, ItemTimingReview
from app.services.analyzer import hero_name, player_team

CHECKPOINTS = [10, 15, 20, 25]

ITEM_LABELS = {
    "abyssal_blade": "Abyssal Blade",
    "aeon_disk": "Aeon Disk",
    "aghanims_shard": "Aghanim's Shard",
    "aghanims_scepter": "Aghanim's Scepter",
    "armlet": "Armlet",
    "assault": "Assault Cuirass",
    "bfury": "Battle Fury",
    "black_king_bar": "Black King Bar",
    "blink": "Blink Dagger",
    "bloodthorn": "Bloodthorn",
    "broadsword": "Broadsword",
    "butterfly": "Butterfly",
    "crimson_guard": "Crimson Guard",
    "daedalus": "Daedalus",
    "dagon": "Dagon",
    "desolator": "Desolator",
    "diffusal_blade": "Diffusal Blade",
    "dust": "Dust",
    "ethereal_blade": "Ethereal Blade",
    "force_staff": "Force Staff",
    "gem": "Gem",
    "glimmer_cape": "Glimmer Cape",
    "guardian_greaves": "Guardian Greaves",
    "heavens_halberd": "Heaven's Halberd",
    "hurricane_pike": "Hurricane Pike",
    "maelstrom": "Maelstrom",
    "mjollnir": "Mjollnir",
    "mask_of_madness": "Mask of Madness",
    "kaya": "Kaya",
    "lesser_crit": "Crystalys",
    "linken_sphere": "Linken's Sphere",
    "lotus_orb": "Lotus Orb",
    "magic_wand": "Magic Wand",
    "manta": "Manta Style",
    "monkey_king_bar": "Monkey King Bar",
    "orchid": "Orchid Malevolence",
    "phase_boots": "Phase Boots",
    "pipe": "Pipe of Insight",
    "power_treads": "Power Treads",
    "radiance": "Radiance",
    "revanants_brooch": "Revenant's Brooch",
    "revenants_brooch": "Revenant's Brooch",
    "rod_of_atos": "Rod of Atos",
    "sange_and_yasha": "Sange and Yasha",
    "satanic": "Satanic",
    "sentry_ward": "Sentry Ward",
    "sheepstick": "Scythe of Vyse",
    "silver_edge": "Silver Edge",
    "skadi": "Eye of Skadi",
    "sphere": "Linken's Sphere",
    "travel_boots": "Boots of Travel",
    "ultimate_scepter": "Aghanim's Scepter",
    "vanguard": "Vanguard",
    "yasha": "Yasha",
}

THREAT_ITEMS = {
    "Physical burst": {"desolator", "bfury", "daedalus", "lesser_crit", "monkey_king_bar", "butterfly", "silver_edge"},
    "Magic burst": {"dagon", "kaya", "ethereal_blade", "revenants_brooch", "revanants_brooch", "radiance"},
    "Catch or silence": {"orchid", "bloodthorn", "sheepstick", "rod_of_atos", "gleipnir", "abyssal_blade", "blink"},
}

ANSWER_ITEMS = {
    "Defensive answer": {
        "black_king_bar",
        "manta",
        "sphere",
        "linken_sphere",
        "sange_and_yasha",
        "butterfly",
        "satanic",
        "aeon_disk",
    },
    "Support save": {"force_staff", "glimmer_cape", "guardian_greaves", "lotus_orb", "pipe", "crimson_guard", "heavens_halberd"},
    "Detection": {"dust", "sentry_ward", "gem"},
}

PLAYER_PROGRESS_ITEMS = {
    "phase_boots",
    "power_treads",
    "travel_boots",
    "magic_wand",
    "vanguard",
    "mask_of_madness",
    "maelstrom",
    "mjollnir",
    "diffusal_blade",
    "dragon_lance",
    "hurricane_pike",
    "yasha",
    "bfury",
    "desolator",
    "blink",
    "radiance",
    "aghanims_shard",
    "aghanims_scepter",
    "ultimate_scepter",
}

IMPORTANT_ITEMS = set().union(*THREAT_ITEMS.values(), *ANSWER_ITEMS.values(), PLAYER_PROGRESS_ITEMS)


def _label(item_key: str) -> str:
    return ITEM_LABELS.get(item_key, item_key.replace("_", " ").title())


def _purchases_by_minute(player: dict, minute: int) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for purchase in player.get("purchase_log") or []:
        item_key = str(purchase.get("key") or "")
        time = int(purchase.get("time") or 0)
        if not item_key or time < 0 or time > minute * 60 or item_key not in IMPORTANT_ITEMS or item_key in seen:
            continue
        seen.add(item_key)
        items.append(item_key)
    return items


def _category_hits(items: set[str], categories: dict[str, set[str]]) -> list[str]:
    return [category for category, keys in categories.items() if items & keys]


def _enemy_key_items(match: dict, player_slot: int, minute: int) -> list[tuple[str, str]]:
    player_side = player_team(player_slot)
    result: list[tuple[str, str]] = []
    for player in match.get("players", []):
        slot = int(player.get("player_slot", 0))
        if player_team(slot) == player_side:
            continue
        hero = hero_name(player.get("hero_id"))
        for item_key in _purchases_by_minute(player, minute):
            if any(item_key in keys for keys in THREAT_ITEMS.values()):
                result.append((hero, item_key))
    return result


def _advice(role: str, threats: list[str], answers: list[str], enemy_items: list[str]) -> str:
    is_support = role in {"Soft Support", "Hard Support"}
    if not threats:
        return "No major enemy item threat was confirmed by this minute, so keep building toward your role timing."
    if answers:
        answer_text = ", ".join(answers)
        return f"You had a confirmed answer category ready: {answer_text}. Next time, play fights around that item cooldown instead of forcing when it is unavailable."
    if is_support:
        return (
            "The enemy item timing created danger before a clear save item was ready. Next match, consider earlier Force Staff, "
            "Glimmer Cape, Lotus, Pipe, or play farther back until your save is ready."
        )
    if "Catch or silence" in threats:
        return (
            "The enemy had catch or silence pressure before a clear defensive answer was ready. Next match, consider BKB, Manta, "
            "Linken, or avoid optional fights until your team can cover you."
        )
    if "Magic burst" in threats:
        return (
            "The enemy magic burst timing was online before a clear defensive answer was ready. Next match, respect that window "
            "and consider BKB, Pipe support, or waiting for a safer timing."
        )
    return (
        "The enemy damage timing was online before a clear defensive answer was ready. Next match, avoid optional fights until "
        "your next survivability item or team save is ready."
    )


def build_item_timing_review(match: dict, metrics: dict) -> ItemTimingReview | None:
    if not metrics.get("is_parsed"):
        return None

    player = next(
        (item for item in match.get("players", []) if int(item.get("player_slot", -1)) == int(metrics["player_slot"])),
        None,
    )
    if not player or not player.get("purchase_log"):
        return None

    checkpoints: list[ItemTimingCheckpoint] = []
    for minute in CHECKPOINTS:
        player_item_keys = _purchases_by_minute(player, minute)
        enemy_pairs = _enemy_key_items(match, int(metrics["player_slot"]), minute)
        enemy_item_keys = {item_key for _, item_key in enemy_pairs}
        player_item_set = set(player_item_keys)
        threats = _category_hits(enemy_item_keys, THREAT_ITEMS)
        answers = _category_hits(player_item_set, ANSWER_ITEMS)
        if not threats and not player_item_keys:
            continue
        enemy_items = [f"{_label(item_key)} on {hero}" for hero, item_key in enemy_pairs[:5]]
        checkpoints.append(
            ItemTimingCheckpoint(
                minute=minute,
                player_items=[_label(item_key) for item_key in player_item_keys],
                enemy_key_items=enemy_items,
                enemy_threats=threats,
                player_answers=answers,
                advice=_advice(str(metrics["role"]), threats, answers, enemy_items),
                confidence="high" if enemy_items else "medium",
            )
        )

    if not checkpoints:
        return None

    first_threat = next((checkpoint for checkpoint in checkpoints if checkpoint.enemy_threats), checkpoints[0])
    if first_threat.enemy_threats:
        main_lesson = (
            f"By {first_threat.minute} minutes, the enemy showed {', '.join(first_threat.enemy_threats).lower()} "
            "pressure. Your next item decision should respect that timing before optional fights."
        )
    else:
        main_lesson = "Your item timing had confirmed purchases, but no major enemy item threat was visible in the checked windows."

    return ItemTimingReview(
        main_lesson=main_lesson,
        checkpoints=checkpoints[:4],
        next_match_item_lesson=checkpoints[-1].advice,
        limitations=[
            "This item review only uses parsed purchase timing from OpenDota.",
            "It does not claim an item caused a death unless fight evidence separately confirms it.",
        ],
    )
