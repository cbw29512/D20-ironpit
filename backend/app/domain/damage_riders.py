from __future__ import annotations

from pydantic import BaseModel, Field


class OncePerTurnWeaponHitDamageRider(BaseModel):
    """Immutable source data for one generic once-per-turn weapon-hit damage rider."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: str = Field(min_length=1)
