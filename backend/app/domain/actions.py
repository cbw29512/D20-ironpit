from __future__ import annotations

from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.hp_threshold_actions import HpThresholdInstantDeathAction
from app.domain.save_damage import DamageTypeName, SaveDamageComponent
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting
from app.domain.environment_contexts import EnvironmentContextId

from app.domain.action_types import (
    AbilityName, ActionCost, HealingTargetMode, ConditionRemovalTargetMode,
    ConditionReactionTrigger, ConditionTiming, ConditionName,
)
from app.domain.healing_actions import HealingAction

class GrapplePeriodicDamage(BaseModel):
    source_name: str = Field(min_length=1)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageTypeName


class GrappleSource(BaseModel):
    source_id: str
    escape_dc: int = Field(ge=1, le=40)
    range_ft: int = Field(default=5, ge=0)
    restrains: bool = False
    source_is_magical: bool = False
    periodic_damage: GrapplePeriodicDamage | None = None


class HitControlEffect(BaseModel):
    max_target_size: CreatureSize | None = None
    grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    restrains_while_grappled: bool = False
    grapple_requires_source_free: bool = False
    grapple_periodic_damage: GrapplePeriodicDamage | None = None
    condition_id: ConditionName | None = None
    expires_at_start_of_source_turn: bool = False
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    allowed_removal_action_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_condition_lifecycle(self) -> "HitControlEffect":
        repeat_fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in repeat_fields) and not all(item is not None for item in repeat_fields):
            raise ValueError("Repeat-save condition lifecycle requires ability, DC, and timing together.")
        if self.expires_at_start_of_source_turn and self.expiry_timing not in {None, "source_turn_start"}:
            raise ValueError("Legacy source-start expiry conflicts with explicit condition timing.")
        return self




class ConditionRemovalAction(BaseModel):
    """A 2024 spell/feature that can legally end one or more named conditions."""

    id: str
    name: str
    action_cost: ActionCost
    range_ft: int = Field(default=5, ge=0)
    target_mode: ConditionRemovalTargetMode = "self_or_ally"
    removable_conditions: list[ConditionName] = Field(default_factory=list)
    requires_explicit_effect_permission: bool = False
    excluded_creature_types: list[str] = Field(default_factory=list)
    max_conditions_per_use: int = Field(default=1, ge=1, le=16)
    resource_costs: dict[str, int] = Field(default_factory=dict)
    resource_costs_per_condition: dict[str, int] = Field(default_factory=dict)
    reaction_trigger: ConditionReactionTrigger | None = None
    expends_spell_slot: bool = False
    reduces_exhaustion_levels: int = Field(default=0, ge=0, le=6)
    removes_curses: bool = False
    removes_all_curses: bool = False
    removes_ability_score_reductions: bool = False
    removes_hit_point_maximum_reductions: bool = False
    requires_active_effect_id: str | None = None
    ends_required_effect: bool = False
    animation: str = "condition-removal"

    @model_validator(mode="after")
    def validate_costs_and_timing(self) -> "ConditionRemovalAction":
        costs = [*self.resource_costs.values(), *self.resource_costs_per_condition.values()]
        if any(cost <= 0 for cost in costs):
            raise ValueError("Condition-removal resource costs must be positive.")
        if self.action_cost == "reaction" and self.reaction_trigger is None:
            raise ValueError("Reaction condition removal requires an explicit RAW trigger.")
        if self.action_cost != "reaction" and self.reaction_trigger is not None:
            raise ValueError("Only Reaction condition removal can define a reaction trigger.")
        resource_ids = {*self.resource_costs, *self.resource_costs_per_condition}
        has_spell_slot_resource = any(resource_id.startswith("spell-slot-") for resource_id in resource_ids)
        if has_spell_slot_resource != self.expends_spell_slot:
            raise ValueError("Spell-slot resources and expends_spell_slot must agree.")
        if not (
            self.removable_conditions
            or self.reduces_exhaustion_levels
            or self.removes_curses
            or self.removes_all_curses
            or self.removes_ability_score_reductions
            or self.removes_hit_point_maximum_reductions
        ):
            raise ValueError("Condition-removal actions require a removable condition or restoration rider.")
        return self


class AreaHealingRider(BaseModel):
    """Independent healing rolled once for one beneficial target inside the action area."""

    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    healing_bonus: int = Field(default=0, ge=0)



class SavingThrowAction(BaseModel):
    id: str
    name: str
    action_cost: ActionCost = "action"
    save_ability: AbilityName
    save_ability_choices: list[AbilityName] = Field(default_factory=list)
    dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0)
    max_targets: int = Field(default=1, ge=1, le=20)
    target_scope: Literal["enemies", "all-other-creatures"] = Field(
        default="enemies", exclude_if=lambda value: value == "enemies",
    )
    target_max_size: CreatureSize | None = None
    area: AreaTargeting | None = None
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    failure_sets_zero_hp: bool = Field(default=False, exclude_if=lambda value: not value)
    damage_only_on_success: bool = Field(default=False, exclude_if=lambda value: not value)
    damage_components: list[SaveDamageComponent] = Field(default_factory=list)
    grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    restrains_while_grappled: bool = False
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    requires_no_active_grapple: bool = False
    opening_initiative_only: bool = Field(default=False, exclude_if=lambda value: not value)
    magical_effect: bool = False
    effect_tags: list[str] = Field(default_factory=list)
    automatic_failure_creature_types: list[str] = Field(default_factory=list)
    requires_target_hearing: bool = False
    requires_target_to_see_source: bool = Field(default=False, exclude_if=lambda value: not value)
    required_target_condition: ConditionName | None = Field(default=None, exclude_if=lambda value: value is None)
    prohibited_environment_context_id: EnvironmentContextId | None = Field(
        default=None, exclude_if=lambda value: value is None,
    )
    requires_target_sight: bool = False
    failed_save_timed_effect: FailedSaveTimedEffect | None = None
    source_effect_immunity_on_success: bool = False
    failed_save_push_ft: int = Field(default=0, ge=0)
    area_healing_rider: AreaHealingRider | None = None
    required_target_creature_types: list[str] = Field(default_factory=list)
    prohibited_target_source_effect_ids: list[str] = Field(default_factory=list)
    excluded_target_creature_types: list[str] = Field(default_factory=list)
    minimum_remaining_hp: int = Field(default=0, ge=0)
    reduce_hit_point_maximum_on_failed_save: bool = False
    animation: str = "save-effect"

    @model_validator(mode="after")
    def validate_asymmetric_save_outcomes(self) -> "SavingThrowAction":
        if self.save_ability_choices and (len(self.save_ability_choices) < 2 or len(set(self.save_ability_choices)) != len(self.save_ability_choices) or self.save_ability not in self.save_ability_choices):
            raise ValueError("Target-chosen save abilities must be distinct and include the primary ability.")
        if self.damage_only_on_success and self.success_damage != "none":
            raise ValueError("Success-only damage cannot also be halved or suppressed on success.")
        has_damage = bool(self.damage_dice_count or self.damage_components)
        if self.damage_only_on_success and not has_damage:
            raise ValueError("Success-only damage requires printed typed damage.")
        if self.failure_sets_zero_hp and has_damage and not self.damage_only_on_success:
            raise ValueError("Direct zero-HP failure cannot also apply normal failure damage.")
        target_filters = [
            *self.required_target_creature_types,
            *self.prohibited_target_source_effect_ids,
            *self.excluded_target_creature_types,
        ]
        if any(not item.strip() for item in target_filters):
            raise ValueError("Save target filters must be nonblank.")
        return self


class HpThresholdConditionAction(BaseModel):
    """Action that applies a timed condition without an initial save when current HP is low enough."""

    id: str
    name: str
    action_cost: ActionCost = "action"
    range_ft: int = Field(ge=0)
    requires_target_sight: bool = False
    max_current_hp: int = Field(ge=1)
    condition_id: ConditionName
    repeat_save_ability: AbilityName
    repeat_save_dc: int = Field(ge=1, le=40)
    repeat_save_timing: ConditionTiming = "target_turn_end"
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    magical_effect: bool = True
    animation: str = "condition"
