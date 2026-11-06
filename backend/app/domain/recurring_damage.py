"""Generic source-defined recurring damage applied by a successful weapon hit."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.weapons_base import DamageType


class OnHitRecurringDamage(BaseModel):
    """Immutable card parameters, independent of the originating ability name."""

    effect_id: str = Field(min_length=1)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    tick_timing: Literal["target_turn_end"] = "target_turn_end"
    stacking: Literal["nonstacking"] = "nonstacking"
    ends_if_source_dead: bool = False
