from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons import DamageType


class RegenerationDefinition(BaseModel):
    amount: int = Field(gt=0)
    suppressed_by_damage_types: list[DamageType] = Field(default_factory=list)
    delays_death_at_zero: bool = False


class TurnDamageAuraDefinition(BaseModel):
    id: str
    name: str
    radius_ft: int = Field(gt=0)
    dice_count: int = Field(gt=0, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType
    target_mode: Literal["enemies", "all-creatures"] = "enemies"
    suppressed_if_incapacitated: bool = False


class AllyRollAuraDefinition(BaseModel):
    """Passive source-centered roll benefits shared with the source and its allies."""

    id: str
    name: str
    radius_ft: int = Field(gt=0)
    attack_advantage: bool = False
    saving_throw_advantage: bool = False
    suppressed_if_incapacitated: bool = False
