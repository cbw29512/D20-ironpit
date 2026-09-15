from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import DamageTypeName


class SpellDamageComponent(BaseModel):
    """An additional typed damage component resolved by the same spell save."""

    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName
