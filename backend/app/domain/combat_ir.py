from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.areas import AreaTargeting
from app.domain.capability_effects import AttackEffectDefinition, DiceSpec
from app.domain.combat_ir_effects import HealingEffectIR
from app.domain.combat_ir_resolution import (
    AttackRollResolutionIR,
    AutomaticResolutionIR,
    ResolutionIR,
    SavingThrowResolutionIR,
)
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

TargetModeIR = Literal["enemy", "self", "ally", "self_or_ally", "other"]
CombatEffectIR = AttackEffectDefinition | HealingEffectIR


class ResourceCostIR(BaseModel):
    resource_id: str
    amount: int = Field(default=1, ge=1, le=20)


class TargetingIR(BaseModel):
    mode: Literal["single", "area"] = "single"
    range_ft: int = Field(default=5, ge=0)
    area: AreaTargeting | None = None
    max_target_size: CreatureSize | None = None
    target_mode: TargetModeIR = "enemy"

    @model_validator(mode="after")
    def validate_area(self) -> "TargetingIR":
        if (self.mode == "area") != (self.area is not None):
            raise ValueError("Area targeting mode and area geometry must agree.")
        return self


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
    effects: list[CombatEffectIR] = Field(default_factory=list)
    resource_cost: ResourceCostIR | None = None
    animation: str = "action"

    @model_validator(mode="after")
    def validate_cost_and_trigger(self) -> "CombatActionIR":
        if self.action_cost == "reaction" and self.trigger != "reaction":
            raise ValueError("Reaction actions require reaction timing.")
        if self.action_cost != "reaction" and self.trigger == "reaction":
            raise ValueError("Reaction timing requires reaction action cost.")
        return self


__all__ = [
    "AttackRollResolutionIR",
    "AutomaticResolutionIR",
    "CombatActionIR",
    "PrimaryDamageIR",
    "ResourceCostIR",
    "ResolutionIR",
    "SavingThrowResolutionIR",
    "TargetingIR",
]
