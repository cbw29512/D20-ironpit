from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ConditionName
from app.domain.capability_effects import DiceSpec, GrappleEffectDefinition
from app.domain.environment_contexts import EnvironmentContextId
from app.domain.save_damage import SaveDamageComponent
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


class SaveCapabilityDefinition(BaseModel):
    id: str
    name: str
    action_cost: Literal["action", "bonus_action", "reaction"] = "action"
    save_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    save_ability_choices: list[Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]] = Field(default_factory=list)
    dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0)
    max_targets: int = Field(default=1, ge=1, le=20)
    target_scope: Literal["enemies", "all-other-creatures"] = Field(
        default="enemies", exclude_if=lambda value: value == "enemies",
    )
    target_max_size: CreatureSize | None = None
    area: AreaTargeting | None = None
    damage: DiceSpec | None = None
    damage_type: DamageType | None = None
    damage_components: list[SaveDamageComponent] = Field(default_factory=list)
    success_damage: Literal["none", "half"] = "none"
    # Generic damage-linked maximum-HP loss; applies after either save result.
    reduce_hit_point_maximum_on_damage: bool = Field(default=False, exclude_if=lambda value: not value)
    max_hp_zero_kills: bool = Field(default=False, exclude_if=lambda value: not value)
    failure_sets_zero_hp: bool = Field(default=False, exclude_if=lambda value: not value)
    # Generic typed finisher: a living 0-HP creature saves or dies; healing
    # occurs only if that death actually completes (prevention may apply).
    requires_target_zero_hp_alive: bool = False
    instant_death_on_failed_save: bool = False
    heal_source_on_kill_dice_count: int = Field(default=0, ge=0, le=40)
    heal_source_on_kill_dice_size: int = Field(default=6, ge=2, le=100)
    damage_only_on_success: bool = Field(default=False, exclude_if=lambda value: not value)
    requires_target_hearing: bool = Field(default=False, exclude_if=lambda value: not value)
    requires_target_to_see_source: bool = Field(default=False, exclude_if=lambda value: not value)
    requires_target_sight: bool = Field(default=False, exclude_if=lambda value: not value)
    required_target_condition: ConditionName | None = Field(default=None, exclude_if=lambda value: value is None)
    # The live target condition must originate from this save-action actor.
    required_target_source_condition: ConditionName | None = Field(default=None, exclude_if=lambda value: value is None)
    requires_target_grappled_by_source: bool = Field(default=False, exclude_if=lambda value: not value)
    required_target_creature_types: list[str] = Field(default_factory=list, exclude_if=lambda value: not value)
    prohibited_target_source_effect_ids: list[str] = Field(default_factory=list, exclude_if=lambda value: not value)
    excluded_target_creature_types: list[str] = Field(default_factory=list, exclude_if=lambda value: not value)
    prohibited_environment_context_id: EnvironmentContextId | None = Field(
        default=None, exclude_if=lambda value: value is None,
    )
    grapple: GrappleEffectDefinition | None = None
    opening_initiative_only: bool = False
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    requires_no_active_grapple: bool = False
    magical_effect: bool = False
    effect_tags: list[str] = Field(default_factory=list)
    failed_save_timed_effect: FailedSaveTimedEffect | None = None
    source_effect_immunity_on_success: bool = False
    source_effect_immunity_keys_on_success: list[str] = Field(default_factory=list)
    source_effect_immunity_keys_blocking: list[str] = Field(default_factory=list)
    failed_save_push_ft: int = Field(default=0, ge=0)
    # Arena-locked forced movement: log leaving the source's occupied square.
    successful_save_exits_source_space: bool = Field(
        default=False, exclude_if=lambda value: not value,
    )
    animation: str = "save-effect"

    @model_validator(mode="after")
    def validate_damage(self) -> "SaveCapabilityDefinition":
        try:
            if (self.damage is None) != (self.damage_type is None):
                raise ValueError("Save damage dice and damage type must be declared together.")
            if self.damage_components and self.damage is not None:
                raise ValueError("Save damage must use either legacy dice or typed components, not both.")
            if self.save_ability_choices and (
                len(self.save_ability_choices) < 2
                or len(set(self.save_ability_choices)) != len(self.save_ability_choices)
                or self.save_ability not in self.save_ability_choices
            ):
                raise ValueError("Target-chosen save abilities must be distinct and include the primary ability.")
            if self.reduce_hit_point_maximum_on_damage and self.damage is None and not self.damage_components:
                raise ValueError("Damage-linked maximum-HP reduction requires a typed save damage roll.")
            if self.max_hp_zero_kills and not self.reduce_hit_point_maximum_on_damage:
                raise ValueError("Terminal maximum-HP loss requires damage-linked maximum-HP reduction.")
            if (self.required_target_condition is not None and self.required_target_source_condition is not None
                and self.required_target_condition != self.required_target_source_condition):
                raise ValueError("Source-owned and unqualified required conditions cannot disagree.")
            if self.damage_only_on_success and self.success_damage != "none":
                raise ValueError("Success-only save damage must not declare legacy success scaling.")
            if self.damage_only_on_success and self.damage is None:
                raise ValueError("Success-only save damage requires typed damage dice.")
            if self.failure_sets_zero_hp and self.damage is not None and not self.damage_only_on_success:
                raise ValueError("Zero-HP failure cannot coexist with ordinary failed-save damage.")
            if self.instant_death_on_failed_save:
                if not self.requires_target_zero_hp_alive or not self.heal_source_on_kill_dice_count:
                    raise ValueError("Save-based finisher requires living zero-HP target and explicit on-kill healing dice.")
                if self.damage is not None or self.damage_components or self.failure_sets_zero_hp:
                    raise ValueError("Instant death on a failed save cannot also deal damage or set target to zero HP.")
            elif self.requires_target_zero_hp_alive or self.heal_source_on_kill_dice_count:
                raise ValueError("Zero-HP finisher fields require a failed-save instant-death effect.")
            target_filters = [
                *self.required_target_creature_types,
                *self.prohibited_target_source_effect_ids,
                *self.excluded_target_creature_types,
            ]
            if any(not item.strip() for item in target_filters):
                raise ValueError("Save target filters must be nonblank.")
            immunity_keys = [
                *self.source_effect_immunity_keys_on_success,
                *self.source_effect_immunity_keys_blocking,
            ]
            if any(not item.strip() for item in immunity_keys):
                raise ValueError("Save immunity keys must be nonblank.")
            if self.successful_save_exits_source_space and (
                self.area is None or self.area.shape != "shared-space"
                or self.area.origin != "self"
            ):
                raise ValueError("Successful shared-space exit needs a self shared-space area.")
            if self.grapple and self.grapple.max_target_size and self.target_max_size:
                if self.grapple.max_target_size != self.target_max_size:
                    raise ValueError("Save target size and grapple target size cannot disagree.")
            return self
        except Exception:
            logger.exception("Save capability validation failed for %s.", self.id)
            raise
