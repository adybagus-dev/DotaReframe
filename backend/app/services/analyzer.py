from typing import Optional

from app.schemas.match import PlayerSummary

HERO_NAMES = {
    1: "Anti-Mage", 2: "Axe", 3: "Bane", 4: "Bloodseeker", 5: "Crystal Maiden",
    6: "Drow Ranger", 7: "Earthshaker", 8: "Juggernaut", 9: "Mirana", 10: "Morphling",
    11: "Shadow Fiend", 12: "Phantom Lancer", 13: "Puck", 14: "Pudge", 15: "Razor",
    16: "Sand King", 17: "Storm Spirit", 18: "Sven", 19: "Tiny", 20: "Vengeful Spirit",
    21: "Windranger", 22: "Zeus", 23: "Kunkka", 25: "Lina", 26: "Lion",
    27: "Shadow Shaman", 28: "Slardar", 29: "Tidehunter", 30: "Witch Doctor", 31: "Lich",
    32: "Riki", 33: "Enigma", 34: "Tinker", 35: "Sniper", 36: "Necrophos",
    37: "Warlock", 38: "Beastmaster", 39: "Queen of Pain", 40: "Venomancer",
    41: "Faceless Void", 42: "Wraith King", 43: "Death Prophet", 44: "Phantom Assassin",
    45: "Pugna", 46: "Templar Assassin", 47: "Viper", 48: "Luna", 49: "Dragon Knight",
    50: "Dazzle", 51: "Clockwerk", 52: "Leshrac", 53: "Nature's Prophet", 54: "Lifestealer",
    55: "Dark Seer", 56: "Clinkz", 57: "Omniknight", 58: "Enchantress", 59: "Huskar",
    60: "Night Stalker", 61: "Broodmother", 62: "Bounty Hunter", 63: "Weaver", 64: "Jakiro",
    65: "Batrider", 66: "Chen", 67: "Spectre", 68: "Ancient Apparition", 69: "Doom",
    70: "Ursa", 71: "Spirit Breaker", 72: "Gyrocopter", 73: "Alchemist", 74: "Invoker",
    75: "Silencer", 76: "Outworld Destroyer", 77: "Lycan", 78: "Brewmaster",
    79: "Shadow Demon", 80: "Lone Druid", 81: "Chaos Knight", 82: "Meepo",
    83: "Treant Protector", 84: "Ogre Magi", 85: "Undying", 86: "Rubick", 87: "Disruptor",
    88: "Nyx Assassin", 89: "Naga Siren", 90: "Keeper of the Light", 91: "Io", 92: "Visage",
    93: "Slark", 94: "Medusa", 95: "Troll Warlord", 96: "Centaur Warrunner",
    97: "Magnus", 98: "Timbersaw", 99: "Bristleback", 100: "Tusk", 101: "Skywrath Mage",
    102: "Abaddon", 103: "Elder Titan", 104: "Legion Commander", 105: "Techies",
    106: "Ember Spirit", 107: "Earth Spirit", 108: "Underlord", 109: "Terrorblade",
    110: "Phoenix", 111: "Oracle", 112: "Winter Wyvern", 113: "Arc Warden",
    114: "Monkey King", 119: "Dark Willow", 120: "Pangolier", 121: "Grimstroke",
    123: "Hoodwink", 126: "Void Spirit", 128: "Snapfire", 129: "Mars",
    135: "Dawnbreaker", 136: "Marci", 137: "Primal Beast", 138: "Muerta"
}

LANE_ROLE = {
    1: "Safe Lane",
    2: "Mid Lane",
    3: "Off Lane",
    4: "Jungle"
}


def hero_name(hero_id: Optional[int]) -> str:
    return HERO_NAMES.get(hero_id or 0, f"Hero {hero_id or 'Unknown'}")


def player_team(player_slot: int) -> str:
    return "Radiant" if player_slot < 128 else "Dire"


def player_result(match: dict, player_slot: int) -> str:
    radiant_win = bool(match.get("radiant_win"))
    team = player_team(player_slot)
    won = (team == "Radiant" and radiant_win) or (team == "Dire" and not radiant_win)
    return "Won" if won else "Lost"


def kda(player: dict) -> str:
    return f"{player.get('kills', 0)} / {player.get('deaths', 0)} / {player.get('assists', 0)}"


def build_player_list(match: dict) -> list[dict]:
    match_id = int(match.get("match_id", 0))
    players = []
    for player in match.get("players", []):
        slot = int(player.get("player_slot", 0))
        summary = PlayerSummary(
            match_id=match_id,
            player_slot=slot,
            hero=hero_name(player.get("hero_id")),
            team=player_team(slot),
            result=player_result(match, slot),
            role=LANE_ROLE.get(player.get("lane_role")),
            kda=kda(player),
            gpm=int(player.get("gold_per_min") or 0),
        )
        players.append(summary.model_dump())
    return players


def calculate_player_metrics(match: dict, player_slot: int) -> dict:
    player = next((item for item in match.get("players", []) if int(item.get("player_slot", -1)) == player_slot), None)
    if player is None:
        raise ValueError("Player slot not found in match")

    duration_minutes = round((match.get("duration") or 0) / 60)
    team_kills = sum(
        item.get("kills", 0)
        for item in match.get("players", [])
        if player_team(int(item.get("player_slot", 0))) == player_team(player_slot)
    )
    participation = 0
    if team_kills:
        participation = round((player.get("kills", 0) + player.get("assists", 0)) / team_kills * 100)

    return {
        "match_id": int(match.get("match_id", 0)),
        "player_slot": player_slot,
        "hero": hero_name(player.get("hero_id")),
        "role": LANE_ROLE.get(player.get("lane_role")) or "Unknown Role",
        "result": player_result(match, player_slot),
        "duration_minutes": duration_minutes,
        "kills": int(player.get("kills") or 0),
        "deaths": int(player.get("deaths") or 0),
        "assists": int(player.get("assists") or 0),
        "kda": kda(player),
        "gpm": int(player.get("gold_per_min") or 0),
        "xpm": int(player.get("xp_per_min") or 0),
        "last_hits": int(player.get("last_hits") or 0),
        "denies": int(player.get("denies") or 0),
        "hero_damage": int(player.get("hero_damage") or 0),
        "tower_damage": int(player.get("tower_damage") or 0),
        "healing": int(player.get("hero_healing") or 0),
        "level": int(player.get("level") or 0),
        "kill_participation": participation,
    }
