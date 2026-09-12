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
    failure_push_ft: int = Field(default=0, ge=0, le=120)
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: str | None = None
    success_damage: Literal["none", "half"] = "none"
    zero_hp_stable: bool = False
    zero_hp_condition_ids: list[ConditionName] = Field(default_factory=list)
    zero_hp_duration_rounds: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_effect(self) -> "OnHitSaveEffect":
        if self.failure_push_ft % 5:
            raise ValueError("On-hit forced movement must use 5-foot increments.")
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("On-hit save damage requires a damage type.")
        if self.condition_id is None and self.damage_dice_count == 0 and self.failure_push_ft == 0:
            raise ValueError("On-hit save effect requires a condition, damage, or forced movement.")
        if self.zero_hp_stable:
            if self.damage_dice_count == 0 or not self.zero_hp_condition_ids or self.zero_hp_duration_rounds is None:
                raise ValueError("Stable zero-HP rider requires save damage, conditions, and duration.")
        elif self.zero_hp_condition_ids or self.zero_hp_duration_rounds is not None:
            raise ValueError("Zero-HP rider details require zero_hp_stable.")
        return self