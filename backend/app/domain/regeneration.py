from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class RegenerationRule(BaseModel):
    hit_points: int = Field(ge=1, le=500)
    suppressed_by_damage_types: list[DamageType] = Field(default_factory=list)
    dies_at_start_turn_if_zero_and_suppressed: bool = False
