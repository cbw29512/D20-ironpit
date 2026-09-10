from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName
from app.domain.capability_effects import (
    AttackEffectDefinition,
    DiceSpec,
    GrappleEffectDefinition,
    SaveFailureEffectDefinition,
)
from app.domain.charge import ChargeProfile
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting
from app.domain.weapons import ConditionalAttackAdvantage, DamageType, WeaponAttackKind


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
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    rage_eligible: bool = False
    conditional_attack_advantage: list[ConditionalAttackAdvantage] = Field(default_factory=list)
    effects: list[AttackEffectDefinition] = Field(default_factory=list)
    charge_profile: ChargeProfile | None = None
    push_target_away_ft: int = Field(default=0, ge=0, le=120)
    push_target_max_size: CreatureSize | None = None
    pull_target_toward_ft: int = Field(default=0, ge=0, le=120)
    pull_target_max_size: CreatureSize | None = None
    forbid_target_grappled_by_self: bool = False

    @model_validator(mode="after")
    def validate_attack_shape(self) -> "AttackCapabilityDefinition":
        if self.damage is not None and self.fixed_damage is not None:
            raise ValueError("Attack cannot declare both rolled and fixed damage.")
        if self.damage is None and self.fixed_damage is None and not self.effects:
            raise ValueError("Damage-free attack requires at least one on-hit effect.")
        if self.attack_kind in {WeaponAttackKind.RANGED, WeaponAttackKind.MELEE_OR_RANGED} and (
            self.normal_range_ft is None or self.long_range_ft is None
        ):
            raise ValueError("Ranged-capable attack requires normal and long range.")
        if self.attack_ability_modifier is not None and self.attack_ability is None:
            raise ValueError("Attack ability modifier requires an explicit attack ability.")
        if self.push_target_away_ft and self.pull_target_toward_ft:
            raise ValueError("An attack cannot both push and pull the same target on hit.")
        if self.push_target_max_size is not None and self.push_target_away_ft == 0:
            raise ValueError("Push target size requires a positive push distance.")
        if self.pull_target_max_size is not None and self.pull_target_toward_ft == 0:
            raise ValueError("Pull target size requires a positive pull distance.")
        if self.push_target_away_ft % 5 or self.pull_target_toward_ft % 5:
            raise ValueError("Forced movement distance must use 5-foot increments.")
        control_count = sum(effect.kind in {"grapple", "condition"} for effect in self.effects)
        if control_count > 1:
            raise ValueError("Current runtime supports one persistent control rider per attack.")
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
    failure_effects: list[SaveFailureEffectDefinition] = Field(default_factory=list)
    push_target_away_ft: int = Field(default=0, ge=0, le=200)
    push_target_max_size: CreatureSize | None = None
    grapple: GrappleEffectDefinition | None = None
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    animation: str = "save-effect"

    @model_validator(mode="after")
    def validate_damage(self) -> "SaveCapabilityDefinition":
        if (self.damage is None) != (self.damage_type is None):
            raise ValueError("Save damage dice and damage type must be declared together.")
        if self.grapple and self.grapple.max_target_size and self.target_max_size:
            if self.grapple.max_target_size != self.target_max_size:
                raise ValueError("Save target size and grapple target size cannot disagree.")
        if self.grapple and any(effect.kind == "grapple" for effect in self.failure_effects):
            raise ValueError("Use either legacy grapple or failure_effects grapple, not both.")
        if self.push_target_max_size is not None and self.push_target_away_ft <= 0:
            raise ValueError("Save-action push size limit requires positive push distance.")
        if self.push_target_away_ft % 5:
            raise ValueError("Save-action forced movement must use 5-foot increments.")
        return self


class CapabilityActionSlot(BaseModel):
    attack_ids: list[str] = Field(default_factory=list, max_length=16)
    save_action_ids: list[str] = Field(default_factory=list, max_length=16)
    forced_movement_action_ids: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def require_choice(self) -> "CapabilityActionSlot":
        if not self.attack_ids and not self.save_action_ids and not self.forced_movement_action_ids:
            raise ValueError("Attack-action slot requires an attack, save, or forced-movement action.")
        return self


class MultiattackCapabilityDefinition(BaseModel):
    id: str
    name: str = "Multiattack"
    is_attack_action: bool = False
    slots: list[CapabilityActionSlot] = Field(min_length=1, max_length=8)
