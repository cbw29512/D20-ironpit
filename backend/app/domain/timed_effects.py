from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.damage_types import DamageType
from app.domain.rule_types import AbilityName, ConditionName, ConditionTiming

TimedTurnBehavior = Literal["normal", "forced_retreat"]


class TimedEffect(BaseModel):
    effect_id: str
    source_id: str
    source_effect_id: str | None = None
    effect_family: str | None = None
    applied_round: int | None = Field(default=None, ge=1)
    expires_round: int | None = Field(default=None, ge=1)
    expires_at_start_of_source_turn: bool = True
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_eligible_round: int | None = Field(default=None, ge=1)
    repeat_save_failure_condition: ConditionName | None = None
    repeat_save_failure_continues: bool = True
    repeat_save_failure_duration_rounds: int | None = Field(default=None, ge=1, le=100)
    repeat_save_failure_ends_on_damage: bool = False
    repeat_save_failure_allowed_removal_action_ids: list[str] = Field(default_factory=list)
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    periodic_damage_timing: Literal["target_turn_start", "target_turn_end"] | None = None
    periodic_damage_dice_count: int = Field(default=0, ge=0, le=40)
    periodic_damage_dice_size: int = Field(default=6, ge=2, le=100)
    periodic_damage_bonus: int = 0
    periodic_damage_type: DamageType | None = None
    turn_behavior: TimedTurnBehavior = "normal"
    action_or_bonus_only: bool = False
    reactions_disabled: bool = False
    speed_multiplier: float = Field(default=1.0, gt=0, le=1.0)
    d20_disadvantage_ability: AbilityName | None = None
    damage_penalty_dice_count: int = Field(default=0, ge=0, le=4)
    damage_penalty_dice_size: int = Field(default=6, ge=2, le=20)
    automatic_success_round: int | None = Field(default=None, ge=1)
    requires_active_effect_id: str | None = None
    ends_on_damage: bool = False
    ends_on_owner_attack: bool = False
    ends_on_owner_spell_cast: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "TimedEffect":
        repeat_fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in repeat_fields) and not all(item is not None for item in repeat_fields):
            raise ValueError("Timed effect repeat save requires ability, DC, and timing together.")
        if self.repeat_save_eligible_round is not None and not all(item is not None for item in repeat_fields):
            raise ValueError("Repeat-save eligibility requires a complete repeat-save rule.")
        if self.repeat_save_failure_condition is not None and not all(item is not None for item in repeat_fields):
            raise ValueError("Repeat-save failure condition requires a complete repeat-save rule.")
        transition_options = (
            not self.repeat_save_failure_continues,
            self.repeat_save_failure_duration_rounds is not None,
            self.repeat_save_failure_ends_on_damage,
            bool(self.repeat_save_failure_allowed_removal_action_ids),
        )
        if any(transition_options) and self.repeat_save_failure_condition is None:
            raise ValueError("Second-stage runtime policy requires a repeat-save failure condition.")
        periodic = (self.periodic_damage_timing, self.periodic_damage_type)
        if any(item is not None for item in periodic) and not all(item is not None for item in periodic):
            raise ValueError("Periodic damage requires timing and damage type together.")
        if self.periodic_damage_timing is not None and self.periodic_damage_dice_count < 1:
            raise ValueError("Periodic damage requires at least one damage die.")
        if self.expires_round is not None and self.applied_round is not None and self.expires_round <= self.applied_round:
            raise ValueError("Timed effect expiry round must follow its applied round.")
        if self.automatic_success_round is not None and self.applied_round is not None and self.automatic_success_round <= self.applied_round:
            raise ValueError("Automatic-success round must follow application.")
        if self.expiry_timing is not None:
            self.expires_at_start_of_source_turn = self.expiry_timing == "source_turn_start"
        return self
