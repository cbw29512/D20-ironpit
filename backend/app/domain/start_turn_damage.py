from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class StartTurnRelationshipDamage(BaseModel):
    id: str
    name: str
    target_relationship: Literal["grapplers"]
    dice_count: int = Field(ge=0, le=100)
    dice_size: int = Field(ge=1, le=100)
    damage_bonus: int = Field(default=0, ge=-100, le=100)
    damage_type: DamageType
