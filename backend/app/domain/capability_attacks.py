from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName
from app.domain.capability_effects import AttackEffectDefinition, DiceSpec, GrappleEffectDefinition
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting
from app.domain.weapons import ConditionalAttackAdvantage, DamageType, WeaponAttackKind


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
    conditional_attack_advantage: list[ConditionalAttackAdvantage] = Field(default_factory=list)
    effects: list[AttackEffectDefinition] = Field(default_factory=list)
    charge_profile: ChargeProfileDefinition | None = None
    forbid_target_grappled_by_self: bool = False

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
    save_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0)
    target_max_size: CreatureSize | None = None
    area: AreaTargeting | None = None
    damage: DiceSpec | None = None
    damage_type: DamageType | None = None
    success_damage: Literal["none", "half"] = "none"
    grapple: GrappleEffectDefinition | None = None
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    requires_no_active_grapple: bool = False
    magical_effect: bool = False
    animation: str = "save-effect"

    @model_validator(mode="after")
    def validate_damage(self) -> "SaveCapabilityDefinition":
        if (self.damage is None) != (self.damage_type is None):
            raise ValueError("Save damage dice and damage type must be declared together.")
        if self.grapple and self.grapple.max_target_size and self.target_max_size:
            if self.grapple.max_target_size != self.target_max_size:
                raise ValueError("Save target size and grapple target size cannot disagree.")
        return self


class CapabilityActionSlot(BaseModel):
    attack_ids: list[str] = Field(default_factory=list, max_length=16)
    save_action_ids: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def require_choice(self) -> "CapabilityActionSlot":
        if not self.attack_ids and not self.save_action_ids:
            raise ValueError("Attack-action slot requires an attack or save action.")
        return self


class MultiattackCapabilityDefinition(BaseModel):
    id: str
    name: str = "Multiattack"
    is_attack_action: bool = False
    slots: list[CapabilityActionSlot] = Field(min_length=1, max_length=8)
