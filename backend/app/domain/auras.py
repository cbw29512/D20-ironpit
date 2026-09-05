from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class EndTurnDamageAura(BaseModel):
    name: str
    radius_ft: int = Field(ge=0)
    dice_count: int = Field(ge=1)
    dice_size: int = Field(ge=2)
    damage_bonus: int = 0
    damage_type: DamageType
    target_mode: Literal["enemies", "all_others"] = "enemies"
    disabled_while_incapacitated: bool = False
