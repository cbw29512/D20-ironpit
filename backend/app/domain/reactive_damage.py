from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class MeleeHitReactiveDamage(BaseModel):
    id: str = Field(min_length=1)
    range_ft: int = Field(default=5, ge=0, le=60)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType
