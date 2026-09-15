from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.size import CreatureSize


class SaveFailureMarginEscalation(BaseModel):
    margin: int = Field(ge=1, le=40)
    additional_condition_ids: list[ConditionName] = Field(min_length=1)
    replacement_duration_rounds: int | None = Field(default=None, ge=1)
    replacement_duration_dice_count: int = Field(default=0, ge=0, le=20)
    replacement_duration_dice_size: int = Field(default=6, ge=2, le=100)
    replacement_duration_round_multiplier: int = Field(default=1, ge=1, le=600)
    ends_on_damage: bool = False
    allowed_removal_action_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_duration(self) -> "SaveFailureMarginEscalation":
        if self.replacement_duration_rounds is not None and self.replacement_duration_dice_count:
            raise ValueError("Failure-margin escalation cannot define fixed and rolled replacement durations together.")
        return self


class OnHitSaveEffect(BaseModel):
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition_id: ConditionName | None = None
    max_target_size: CreatureSize | None = None
    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_creature_subtypes: list[str] = Field(default_factory=list)
    duration_rounds: int | None = Field(default=None, ge=1)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_failure_condition_id: ConditionName | None = None
    failure_margin_escalation: SaveFailureMarginEscalation | None = None
    ends_on_damage: bool = False
    failure_push_ft: int = Field(default=0, ge=0, le=120)
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: str | None = None
    success_damage: Literal["none", "half"] = "none"
    gates_ongoing_damage: bool = False
    swallow_on_failure: bool = False
    max_hp_reduction_equals_damage_taken: bool = False
    zero_max_hp_kills: bool = False
    zero_hp_stable: bool = False
    zero_hp_condition_ids: list[ConditionName] = Field(default_factory=list)
    zero_hp_duration_rounds: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_effect(self) -> "OnHitSaveEffect":
        if self.failure_push_ft % 5:
            raise ValueError("On-hit forced movement must use 5-foot increments.")
        if self.damage_dice_count and self.damage_type is None:
            raise ValueError("On-hit save damage requires a damage type.")
        has_outcome = (
            self.condition_id is not None or self.damage_dice_count > 0 or self.failure_push_ft > 0
            or self.max_hp_reduction_equals_damage_taken or self.gates_ongoing_damage or self.swallow_on_failure
        )
        if not has_outcome:
            raise ValueError("On-hit save effect requires a certified failed-save outcome.")
        if self.failure_margin_escalation is not None and self.condition_id is None:
            raise ValueError("Failure-margin escalation requires a primary failed-save condition.")
        if self.zero_max_hp_kills and not self.max_hp_reduction_equals_damage_taken:
            raise ValueError("Zero maximum-HP death requires a maximum-HP reduction rider.")
        if self.repeat_save_failure_condition_id is not None and self.repeat_save_timing is None:
            raise ValueError("On-hit staged escalation requires repeat-save timing.")
        if self.zero_hp_stable:
            if self.damage_dice_count == 0 or not self.zero_hp_condition_ids or self.zero_hp_duration_rounds is None:
                raise ValueError("Stable zero-HP rider requires save damage, conditions, and duration.")
        elif self.zero_hp_condition_ids or self.zero_hp_duration_rounds is not None:
            raise ValueError("Zero-HP rider details require zero_hp_stable.")
        self.excluded_creature_types = [item.lower() for item in self.excluded_creature_types]
        self.excluded_creature_subtypes = [item.lower() for item in self.excluded_creature_subtypes]
        return self
