from app.services.analyzer import build_player_list, calculate_player_metrics


def sample_match() -> dict:
    return {
        "match_id": 8123456789,
        "duration": 2520,
        "radiant_win": False,
        "players": [
            {
                "player_slot": 0,
                "hero_id": 8,
                "kills": 8,
                "deaths": 7,
                "assists": 11,
                "gold_per_min": 512,
                "xp_per_min": 641,
                "last_hits": 286,
                "denies": 12,
                "hero_damage": 24100,
                "tower_damage": 1240,
                "hero_healing": 0,
                "level": 24,
                "lane_role": 1,
                "account_id": 12345,
                "rank_tier": 54,
                "purchase_log": [{"time": 600, "key": "phase_boots"}],
            },
            {"player_slot": 128, "hero_id": 44, "kills": 15, "deaths": 4, "assists": 10, "gold_per_min": 658},
        ],
    }


def test_build_player_list_returns_ui_friendly_fields() -> None:
    players = build_player_list(sample_match())

    assert players[0]["hero"] == "Juggernaut"
    assert players[0]["team"] == "Radiant"
    assert players[0]["result"] == "Lost"
    assert players[0]["kda"] == "8 / 7 / 11"


def test_calculate_player_metrics() -> None:
    metrics = calculate_player_metrics(sample_match(), 0)

    assert metrics["duration_minutes"] == 42
    assert metrics["hero"] == "Juggernaut"
    assert metrics["gpm"] == 512
    assert metrics["tower_damage"] == 1240
    assert metrics["account_id"] == 12345
    assert metrics["rank_tier"] == 54


def test_calculate_player_metrics_uses_selected_role() -> None:
    metrics = calculate_player_metrics(sample_match(), 0, "Hard Support")

    assert metrics["role"] == "Hard Support"
    assert metrics["detected_lane_role"] == "Safe Lane"
