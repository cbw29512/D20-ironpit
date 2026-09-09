from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName
from app.domain.areas import AreaTargeting
from app.domain.capability_effects import AttackEffectDefinition, DiceSpec
from app.domain.size import CreatureSize
from app.domain.weapons import ConditionalAttackModifier, DamageType, WeaponAttackKind


class ResourceCostIR(BaseModel):
    resource_id: str
    amount: int = Field(default=1, ge=1, le=20)


class TargetingIR(BaseModel):
    mode: Literal["single", "area"] = "single"
    range_ft: int = Field(default=5, ge=0)
    area: AreaTargeting | None = None
    max_target_size: CreatureSize | None = None

    @model_validator(mode="after")
    def validate_area(self) -> "TargetingIR":
        if (self.mode == "area") != (self.area is not None):
            raise ValueError("Area targeting mode and area geometry must agree.")
        return self


class AttackRollResolutionIR(BaseModel):
    kind: Literal["attack_roll"] = "attack_roll"
    attack_kind: WeaponAttackKind
    attack_bonus: int
    weapon_id: str | None = None
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
    conditional_attack_modifiers: list[ConditionalAttackModifier] = Field(default_factory=list)
    forbid_target_grappled_by_self: bool = False

    @model_validator(mode="after")
    def validate_range_and_ability(self) -> "AttackRollResolutionIR":
        if self.attack_kind is WeaponAttackKind.RANGED and (
            self.normal_range_ft is None or self.long_range_ft is None
        ):
            raise ValueError("Ranged attack resolution requires normal and long range.")
        if self.attack_ability_modifier is not None and self.attack_ability is None:
            raise ValueError("Attack ability modifier requires an explicit attack ability.")
        return self


class SavingThrowResolutionIR(BaseModel):
    kind: Literal["saving_throw"] = "saving_throw"
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    success_damage: Literal["none", "half"] = "none"
    magical_effect: bool = False


ResolutionIR = Annotated[
    AttackRollResolutionIR | SavingThrowResolutionIR,
    Field(discriminator="kind"),
]


class PrimaryDamageIR(BaseModel):
    kind: Literal["primary_damage"] = "primary_damage"
    dice: DiceSpec | None = None
    fixed_damage: int | None = Field(default=None, ge=0)
    damage_type: DamageType

    @model_validator(mode="after")
    def validate_amount(self) -> "PrimaryDamageIR":
        if (self.dice is None) == (self.fixed_damage is None):
            raise ValueError("Primary damage requires exactly one dice or fixed value.")
        return self


class CombatActionIR(BaseModel):
    schema_version: Literal[1] = 1
    id: str
    name: str
    action_cost: Literal["action", "bonus_action", "reaction"] = "action"
    trigger: Literal["turn", "reaction"] = "turn"
    targeting: TargetingIR
    resolution: ResolutionIR
    primary_damage: PrimaryDamageIR | None = None
    effects: list[AttackEffectDefinition] = Field(default_factory=list)
    resource_cost: ResourceCostIR | None = None
    animation: str = "action"

    @model_validator(mode="after")
    def validate_cost_and_trigger(self) -> "CombatActionIR":
        if self.action_cost == "reaction" and self.trigger != "reaction":
            raise ValueError("Reaction actions require reaction timing.")
        if self.action_cost != "reaction" and self.trigger == "reaction":
            raise ValueError("Reaction timing requires reaction action cost.")
        return self
