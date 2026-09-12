from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.size import CreatureSize


class OnHitSaveEffect(BaseModel):
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition_id: ConditionName | None = None
    max_target_size: CreatureSize | None = None
    duration_rounds: int | None = Field(default=None, ge=1)
    repeat_save_timing: ConditionTiming | None = None
    ends_on_damage: bool = False
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: str | None = None
    success_damage: Literal["none", "half"] = "none"

    @model_validator(mode="after")
    def validate_effect(self) -> "OnHitSaveEffect":
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("On-hit save damage requires a damage type.")
        if self.condition_id is None and self.damage_dice_count == 0:
            raise ValueError("On-hit save effect requires a condition or damage.")
        return self
