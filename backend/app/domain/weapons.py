from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, HitControlEffect
from app.domain.charge import AttackChargeProfile, ChargeDamage
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.size import CreatureSize
from app.domain.weapons_base import DamageType, WeaponAttackKind
from app.domain.zero_hp_effects import ZeroHpSaveDamageRider


class ConditionalDamage(BaseModel):
    trigger: Literal["attack_advantage", "attacker_bloodied", "target_bloodied"]
    mode: Literal["add", "replace_weapon"] = "add"
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType


class ConditionalAttackAdvantage(BaseModel):
    trigger: Literal["target_not_full_hp"]


class OnHitDamage(BaseModel):
    source: str
    dice_count: int = Field(ge=0, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType

    @model_validator(mode="after")
    def _fixed_damage_requires_positive_amount(self) -> "OnHitDamage":
        if self.dice_count == 0 and self.damage_bonus <= 0:
            raise ValueError("A zero-die on-hit damage rider requires a positive fixed damage amount.")
        return self


class OnHitSaveDamage(BaseModel):
    source: str
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType
    success_damage: Literal["none", "half"] = "half"
    zero_hp_rider: ZeroHpSaveDamageRider | None = None


class OnHitConditionSave(BaseModel):
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition_id: Literal["prone"]
    max_target_size: CreatureSize | None = None


class Weapon(BaseModel):
    id: str
    name: str
    attack_kind: WeaponAttackKind
    dice_count: int = Field(ge=0, le=20)
    dice_size: int = Field(ge=2, le=100)
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


class WeaponAttack(BaseModel):
    id: str
    weapon: Weapon
    attack_bonus: int
    damage_bonus: int
    damage_die_minimum: int | None = Field(default=None, ge=2, le=100)
    attack_ability: AbilityName | None = None
    attack_ability_modifier: int | None = None
    fixed_damage: int | None = Field(default=None, ge=0)
    conditional_damage: list[ConditionalDamage] = Field(default_factory=list)
    conditional_attack_advantage: list[ConditionalAttackAdvantage] = Field(default_factory=list)
    on_hit_damage: list[OnHitDamage] = Field(default_factory=list)
    on_hit_save_damage: OnHitSaveDamage | None = None
    on_hit_condition_save: OnHitConditionSave | None = None
    on_hit_modifier_effects: list[HitModifierEffect] = Field(default_factory=list)
    charge_profile: AttackChargeProfile | None = None
    rage_eligible: bool = False
    sneak_attack_eligible: bool = False
    knocks_prone_max_size: CreatureSize | None = None
    control_effect: HitControlEffect | None = None
    forbid_target_grappled_by_self: bool = False
