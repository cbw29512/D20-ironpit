from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.rule_types import AbilityName
from app.domain.weapons import DamageType


class DeathTriggeredSaveEffect(BaseModel):
    """Immutable combat data for an effect that resolves immediately when its owner dies."""

    id: str
    name: str
    radius_ft: int = Field(gt=0, le=500)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    damage_dice_count: int = Field(ge=1, le=40)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType
    half_damage_on_success: bool = True
