from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionTiming
from app.domain.combatants import DamageType
from app.domain.debuffs import DebuffCounter
from app.domain.movement import MovementModeGrant
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.timed_control_limits import TimedControlLimits

logger = logging.getLogger(__name__)

TimedTurnBehavior = Literal["normal", "forced_retreat", "single_activity"]


class TimedEffect(BaseModel):
    effect_id: str
    source_id: str
    source_effect_id: str | None = None
    applied_round: int | None = Field(default=None, ge=0)
    expires_round: int | None = Field(default=None, ge=1)
    expires_at_start_of_source_turn: bool = True
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    turn_behavior: TimedTurnBehavior = "normal"
    ends_on_damage: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    source_is_magical: bool = False
    repeat_save_context: SavingThrowContext | None = None
    suppress_action: bool = False
    suppress_bonus_action: bool = False
    suppress_reactions: bool = False
    suppress_movement: bool = False
    next_attack_disadvantage: bool = False
    zero_hp_replacement_hp: int = Field(default=0, ge=0)
    # Universal source ownership for temporary typed resistances. This lets a
    # timed effect clean up only the resistance contribution it owns while an
    # overlapping effect that grants the same type remains active.
    owned_damage_resistances: list[DamageType] = Field(default_factory=list)
    # Buff-owned counters describe which debuffs this effect prevents or can
    # clear, including source qualifiers and conditional movement costs.
    owned_debuff_counters: list[DebuffCounter] = Field(default_factory=list)
    owned_movement_mode_grants: list[MovementModeGrant] = Field(default_factory=list)
    removed_from_battlefield: bool = False
    return_damage_dice_count: int = Field(default=0, ge=0)
    return_damage_dice_size: int = Field(default=0, ge=0)
    return_damage_bonus: int = 0
    return_damage_type: DamageType | None = None
    return_damage_excluded_creature_types: list[str] = Field(default_factory=list)
    start_of_turn_dice_count: int = Field(default=0, ge=0, le=40)
    start_of_turn_dice_size: int = Field(default=6, ge=2, le=100)
    start_of_turn_damage_type: DamageType | None = None
    start_of_turn_save_ability: AbilityName | None = None
    start_of_turn_save_dc: int | None = Field(default=None, ge=1, le=40)
    start_of_turn_save_ends: bool = False
    prevent_hit_point_maximum_reduction: bool = False
    repeat_save_failure_count: int = Field(default=0, ge=0)
    repeat_save_failures_to_lock: int | None = Field(default=None, ge=1, le=10)
    repeat_save_failure_condition_id: str | None = None
    escape_check_ability: AbilityName | None = None
    escape_check_dc: int | None = Field(default=None, ge=1, le=40)
    ground_contact: bool = False
    ends_on_teleport: bool = False
    source_effect_immunity_on_end: bool = False
    control_limits: TimedControlLimits | None = None

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "TimedEffect":
        try:
            repeat_fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
            if any(item is not None for item in repeat_fields) and not all(item is not None for item in repeat_fields):
                raise ValueError("Timed effect repeat save requires ability, DC, and timing together.")
            if (self.escape_check_ability is None) != (self.escape_check_dc is None):
                raise ValueError("Timed effect escape check requires ability and DC together.")
            if self.expires_round is not None and self.applied_round is not None and self.expires_round <= self.applied_round:
                raise ValueError("Timed effect expiry round must follow its applied round.")
            if self.expiry_timing is not None:
                self.expires_at_start_of_source_turn = self.expiry_timing == "source_turn_start"
            return self

        except Exception:
            logger.exception("Invalid timed effect lifecycle for %s from %s.", self.effect_id, self.source_id)
            raise
