import httpx

OPENDOTA_MATCH_URL = "https://api.opendota.com/api/matches/{match_id}"


async def fetch_match(match_id: int) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(OPENDOTA_MATCH_URL.format(match_id=match_id))
        response.raise_for_status()
        data = response.json()
    if "players" not in data:
        raise ValueError("OpenDota did not return players for this match")
    return data
