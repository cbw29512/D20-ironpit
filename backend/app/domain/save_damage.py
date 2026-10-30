from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class SaveDamageComponent(BaseModel):
    """One typed damage component belonging to a saving-throw action."""

    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType
