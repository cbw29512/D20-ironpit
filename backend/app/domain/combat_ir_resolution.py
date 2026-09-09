from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName
from app.domain.weapons import ConditionalAttackModifier, WeaponAttackKind


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


class AutomaticResolutionIR(BaseModel):
    kind: Literal["automatic"] = "automatic"


ResolutionIR = Annotated[
    AttackRollResolutionIR | SavingThrowResolutionIR | AutomaticResolutionIR,
    Field(discriminator="kind"),
]
