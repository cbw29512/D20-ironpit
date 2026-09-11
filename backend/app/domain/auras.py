from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.weapons import DamageType


class EndTurnDamageAura(BaseModel):
    """Source-neutral damaging emanation resolved at the end of the owner's turn."""

    id: str
    name: str
    radius_ft: int = Field(gt=0)
    damage_dice_count: int = Field(ge=0)
    damage_dice_size: int = Field(ge=1)
    damage_bonus: int = 0
    damage_type: DamageType
    disabled_while_incapacitated: bool = False


class StartTurnSaveConditionAura(BaseModel):
    """Source-neutral emanation that forces a save when another creature starts its turn nearby."""

    id: str
    name: str
    radius_ft: int = Field(gt=0)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition: ConditionName
    expiry_timing: ConditionTiming = "target_turn_start"
    magical_effect: bool = False
    disabled_while_incapacitated: bool = False
