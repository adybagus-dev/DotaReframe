from __future__ import annotations

import httpx

OPENDOTA_API = "https://api.opendota.com/api"


class OpenDotaError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


async def _get_json(path: str) -> dict | list:
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{OPENDOTA_API}{path}")
    except httpx.TimeoutException as exc:
        raise OpenDotaError("OpenDota took too long to respond. Please try again.", 504) from exc
    except httpx.RequestError as exc:
        raise OpenDotaError("OpenDota is temporarily unreachable. Please try again.", 503) from exc

    if response.status_code == 404:
        raise OpenDotaError("That public match or player could not be found on OpenDota.", 404)
    if response.status_code == 429:
        raise OpenDotaError("OpenDota is busy right now. Wait a moment and try again.", 503)
    if response.status_code >= 500:
        raise OpenDotaError("OpenDota is temporarily unavailable. Please try again.", 503)
    if response.status_code >= 400:
        raise OpenDotaError("OpenDota could not process this request.", 502)

    try:
        return response.json()
    except ValueError as exc:
        raise OpenDotaError("OpenDota returned an unreadable response.", 502) from exc


async def fetch_match(match_id: int) -> dict:
    from app.services.storage import get_cached_match, save_cached_match

    cached = get_cached_match(match_id)
    if cached:
        return cached

    try:
        data = await _get_json(f"/matches/{match_id}")
    except OpenDotaError:
        stale = get_cached_match(match_id, allow_stale=True)
        if stale:
            return stale
        raise
    if not isinstance(data, dict) or not data.get("players"):
        raise OpenDotaError(
            "OpenDota found the match but player data is not ready yet. Try again after the replay is parsed.",
            422,
        )
    save_cached_match(match_id, data)
    return data


async def fetch_recent_matches(account_id: int) -> list[dict]:
    data = await _get_json(f"/players/{account_id}/recentMatches")
    if not isinstance(data, list):
        raise OpenDotaError("OpenDota returned an unreadable recent-match list.", 502)
    return data
