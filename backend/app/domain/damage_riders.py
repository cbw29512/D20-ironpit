from __future__ import annotations

from pydantic import BaseModel, Field


class OncePerTurnWeaponHitDamageRider(BaseModel):
    """Source-owned generic damage dice added to one successful weapon hit per turn."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: str = Field(min_length=1)
