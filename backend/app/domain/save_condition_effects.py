from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.combatants import DamageType
from app.domain.failure_margin import FailureMarginEscalation, require_escalation_duration
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


class OngoingHpLossEffectDefinition(BaseModel):
    """Immutable attack-source data; the encounter owns the live wound state."""

    kind: Literal["ongoing_hp_loss"] = "ongoing_hp_loss"
    effect_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    excluded_creature_types: list[str] = Field(default_factory=list)
    stacks_on_reapply: bool = True
    ends_on_magical_healing: bool = True


class SaveConditionEffectDefinition(BaseModel):
    kind: Literal["save_condition"] = "save_condition"
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition: ConditionName
    max_target_size: CreatureSize | None = None
    duration_rounds: int | None = Field(default=None, ge=1, le=100800)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_failure_condition: ConditionName | None = None
    failure_push_ft: int = Field(default=0, ge=0)
    cannot_regain_hit_points: bool = False
    start_of_turn_damage_dice_count: int = Field(default=0, ge=0, le=40)
    start_of_turn_damage_dice_size: int = Field(default=6, ge=2, le=100)
    start_of_turn_damage_type: DamageType | None = None
    failure_margin_escalation: FailureMarginEscalation | None = None
    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_creature_subtypes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_condition_lifecycle(self) -> "SaveConditionEffectDefinition":
        try:
            if (
                self.repeat_save_timing is not None
                and self.duration_rounds is None
                and self.repeat_save_failure_condition is None
            ):
                raise ValueError(
                    "Save-condition repeat saves require a duration or a failure escalation condition."
                )
            if self.repeat_save_failure_condition is not None and self.repeat_save_timing is None:
                raise ValueError("Failure escalation requires a repeat-save timing.")
            has_start_damage = self.start_of_turn_damage_dice_count > 0
            if has_start_damage != (self.start_of_turn_damage_type is not None):
                raise ValueError("Start-of-turn condition damage requires both dice and damage type.")
            require_escalation_duration(self.failure_margin_escalation, self.duration_rounds)
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Save-condition lifecycle validation failed.")
            raise ValueError("Save-condition lifecycle could not be validated.") from exc
