from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.failure_margin import FailureMarginEscalation, require_escalation_duration
from app.domain.delayed_effect_transition import DelayedTimedEffectTransition
from app.domain.size import CreatureSize
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class OnHitOngoingHpLoss(BaseModel):
    """Universal on-hit save leading to source-owned, stacking direct HP loss."""

    effect_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    excluded_creature_types: list[str] = Field(default_factory=list)
    stacks_on_reapply: bool = True
    ends_on_magical_healing: bool = True


class OnHitConditionSave(BaseModel):
    model_config = ConfigDict(extra="forbid")

    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition_id: ConditionName | None = None
    effect_id: str | None = Field(default=None, min_length=1)
    curse_id: str | None = Field(default=None, min_length=1)
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    removal_effect_tag: str | None = None
    minimum_removal_spell_level: int = Field(default=0, ge=0, le=9)
    removal_action_exceptions: list[str] = Field(default_factory=list)
    delayed_transition: DelayedTimedEffectTransition | None = None
    max_target_size: CreatureSize | None = None
    duration_rounds: int | None = Field(default=None, ge=1, le=100800)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_failure_condition_id: ConditionName | None = None
    failure_push_ft: int = Field(default=0, ge=0)
    cannot_regain_hit_points: bool = False
    start_of_turn_damage_dice_count: int = Field(default=0, ge=0, le=40)
    start_of_turn_damage_dice_size: int = Field(default=6, ge=2, le=100)
    start_of_turn_damage_type: DamageType | None = None
    failure_margin_escalation: FailureMarginEscalation | None = None
    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_creature_subtypes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_condition_lifecycle(self) -> "OnHitConditionSave":
        try:
            if self.condition_id is None and self.effect_id is None:
                raise ValueError("On-hit save requires a condition or persistent effect id.")
            if self.curse_id is not None and self.effect_id is None:
                raise ValueError("A curse-linked on-hit save requires a persistent effect id.")
            if any(not item.strip() for item in self.allowed_removal_action_ids):
                raise ValueError("Removal action ids must be nonblank.")
            if self.minimum_removal_spell_level and not self.removal_effect_tag:
                raise ValueError("Minimum removal spell level requires an effect tag.")
            if self.repeat_save_failure_condition_id is not None and self.repeat_save_timing is None:
                raise ValueError("Failure escalation requires a repeat-save timing.")
            has_start_damage = self.start_of_turn_damage_dice_count > 0
            if has_start_damage != (self.start_of_turn_damage_type is not None):
                raise ValueError("Start-of-turn condition damage requires both dice and damage type.")
            require_escalation_duration(self.failure_margin_escalation, self.duration_rounds)
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("On-hit condition lifecycle validation failed.")
            raise ValueError("On-hit condition lifecycle could not be validated.") from exc
