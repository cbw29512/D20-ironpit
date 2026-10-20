from __future__ import annotations

from typing import Literal
from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName
from app.domain.capability_effects import AttackEffectDefinition, DiceSpec, GrappleEffectDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.save_damage import SaveDamageComponent
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting
from app.domain.environment_contexts import EnvironmentContextId
from app.domain.weapons import (
    ConditionalAttackAdvantage,
    DamageSourceQualifier,
    DamageType,
    WeaponAttackKind,
)


class ChargeDamageDefinition(BaseModel):
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    damage_bonus: int = 0


class ChargeProfileDefinition(BaseModel):
    minimum_move_ft: int = Field(ge=0)
    max_target_size: CreatureSize | None = None
    prone_max_target_size: CreatureSize | None = None
    prone_save_ability: AbilityName | None = None
    prone_save_dc: int | None = Field(default=None, ge=1, le=40)
    bonus_damage: ChargeDamageDefinition | None = None
    replacement_damage: ChargeDamageDefinition | None = None
    follow_up_attack_id: str | None = None
    follow_up_required_target_condition: ConditionName | None = None
    follow_up_action_cost: Literal["free", "bonus_action"] = "free"

    @model_validator(mode="after")
    def validate_shape(self) -> "ChargeProfileDefinition":
        if (self.prone_save_ability is None) != (self.prone_save_dc is None):
            raise ValueError("Charge Prone save ability and DC must be declared together.")
        if self.follow_up_attack_id is None and (
            self.follow_up_required_target_condition is not None or self.follow_up_action_cost != "free"
        ):
            raise ValueError("Charge follow-up requirements need a follow-up attack id.")
        return self


class AttackCapabilityDefinition(BaseModel):
    id: str
    name: str
    weapon_id: str | None = None
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=1000)
    unavailable_reason: str | None = None
    attack_kind: WeaponAttackKind
    attack_bonus: int
    damage: DiceSpec | None = None
    fixed_damage: int | None = Field(default=None, ge=0)
    damage_type: DamageType
    animation: str
    reach_ft: int = Field(default=5, ge=0)
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)
    projectile: str | None = None
    mastery_property: str | None = None
    light: bool = False
    finesse: bool = False
    heavy: bool = False
    two_handed: bool = False
    versatile: bool = False
    attack_ability: AbilityName | None = None
    attack_ability_modifier: int | None = None
    rage_eligible: bool = False
    sneak_attack_eligible: bool = False
    conditional_attack_advantage: list[ConditionalAttackAdvantage] = Field(default_factory=list)
    effects: list[AttackEffectDefinition] = Field(default_factory=list)
    charge_profile: ChargeProfileDefinition | None = None
    forbid_target_grappled_by_self: bool = False
    grapple_target_policy: Literal["normal", "own_grapple_only", "auto_hit_own_grapple"] = "normal"
    damage_source_qualifiers: list[DamageSourceQualifier] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_attack_shape(self) -> "AttackCapabilityDefinition":
        if (self.damage is None) == (self.fixed_damage is None):
            raise ValueError("Attack must declare exactly one of damage or fixed_damage.")
        if self.attack_kind == WeaponAttackKind.RANGED and (
            self.normal_range_ft is None or self.long_range_ft is None
        ):
            raise ValueError("Ranged attack requires normal and long range.")
        if self.attack_ability_modifier is not None and self.attack_ability is None:
            raise ValueError("Attack ability modifier requires an explicit attack ability.")
        control_count = sum(effect.kind in {"grapple", "condition", "save_condition"} for effect in self.effects)
        if control_count > 1:
            raise ValueError("Current runtime supports one persistent control rider per attack.")
        save_count = sum(effect.kind in {"save_condition", "save_damage"} for effect in self.effects)
        if save_count > 1:
            raise ValueError("Current runtime supports one on-hit saving throw rider per attack.")
        if self.mastery_property == "Topple" and save_count:
            raise ValueError("One attack cannot combine Topple with another on-hit saving throw.")
        return self


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
    failure_sets_zero_hp: bool = Field(default=False, exclude_if=lambda value: not value)
    damage_only_on_success: bool = Field(default=False, exclude_if=lambda value: not value)
    requires_target_hearing: bool = Field(default=False, exclude_if=lambda value: not value)
    requires_target_to_see_source: bool = Field(default=False, exclude_if=lambda value: not value)
    requires_target_sight: bool = Field(default=False, exclude_if=lambda value: not value)
    required_target_condition: ConditionName | None = Field(default=None, exclude_if=lambda value: value is None)
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
    failed_save_push_ft: int = Field(default=0, ge=0)
    animation: str = "save-effect"

    @model_validator(mode="after")
    def validate_damage(self) -> "SaveCapabilityDefinition":
        if (self.damage is None) != (self.damage_type is None):
            raise ValueError("Save damage dice and damage type must be declared together.")
        if self.damage_components and self.damage is not None:
            raise ValueError("Save damage must use either legacy dice or typed components, not both.")
        if self.save_ability_choices and (len(self.save_ability_choices) < 2 or len(set(self.save_ability_choices)) != len(self.save_ability_choices) or self.save_ability not in self.save_ability_choices):
            raise ValueError("Target-chosen save abilities must be distinct and include the primary ability.")
        if self.damage_only_on_success and self.success_damage != "none":
            raise ValueError("Success-only save damage must not declare legacy success scaling.")
        if self.damage_only_on_success and self.damage is None:
            raise ValueError("Success-only save damage requires typed damage dice.")
        if self.failure_sets_zero_hp and self.damage is not None and not self.damage_only_on_success:
            raise ValueError("Zero-HP failure cannot coexist with ordinary failed-save damage.")
        if self.grapple and self.grapple.max_target_size and self.target_max_size:
            if self.grapple.max_target_size != self.target_max_size:
                raise ValueError("Save target size and grapple target size cannot disagree.")
        return self


# Both compilation layers use the same immutable sequence schema.
CapabilityActionSlot = AttackActionSlot


class MultiattackCapabilityDefinition(AttackActionDefinition):
    name: str = "Multiattack"
