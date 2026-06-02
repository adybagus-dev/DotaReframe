from pydantic import BaseModel
from typing import Optional


class PlayerSummary(BaseModel):
    match_id: int
    player_slot: int
    hero: str
    hero_image: Optional[str] = None
    team: str
    result: str
    role: Optional[str] = None
    kda: str
    gpm: int
