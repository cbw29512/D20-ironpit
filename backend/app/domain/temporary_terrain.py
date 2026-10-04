from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.grid import GridPosition


class TemporaryTerrainZone(BaseModel):
    """Mutable per-fight overlay that makes covered cells Difficult Terrain."""

    zone_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    center: GridPosition
    radius_ft: int = Field(ge=5)
    source_is_magical: bool = True
    expires_round: int = Field(ge=2)
    expiry_timing: Literal["source_turn_end"] = "source_turn_end"
