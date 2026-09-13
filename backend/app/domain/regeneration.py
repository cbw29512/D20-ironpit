from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class RegenerationProfile(BaseModel):
    """Data-only start-of-turn regeneration contract."""

    amount: int = Field(ge=1, le=1000)
    requires_positive_hp: bool = False
    suppressed_by_damage_types: list[DamageType] = Field(default_factory=list)
    survives_zero_until_turn: bool = False
