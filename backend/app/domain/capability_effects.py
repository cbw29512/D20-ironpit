from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.domain.attachments import AttachmentEffectDefinition
from app.domain.combatants import DamageType
from app.domain.hit_modifiers import CombatModifierEffect, HitModifierEffect
from app.domain.save_effects import (
    ConditionEffectDefinition,
    GrappleEffectDefinition,
    ProneEffectDefinition,
    SaveFailureEffectDefinition,
)


class DiceSpec(BaseModel):
    count: int = Field(ge=0, le=40)
    size: int = Field(default=6, ge=2, le=100)
    bonus: int = 0


class DamageEffectDefinition(BaseModel):
    kind: Literal["damage"] = "damage"
    source: str
    dice: DiceSpec
    damage_type: DamageType
    trigger: Literal["on_hit", "attack_advantage", "attacker_bloodied", "target_bloodied"] = "on_hit"
    mode: Literal["add", "replace_weapon"] = "add"


class MaxHpReductionEffectDefinition(BaseModel):
    """Reduce max HP by applied attack damage, optionally limited to one damage type."""

    kind: Literal["max-hp-reduction"] = "max-hp-reduction"
    damage_type: DamageType | None = None


AttackEffectDefinition = Annotated[
    DamageEffectDefinition
    | ProneEffectDefinition
    | GrappleEffectDefinition
    | ConditionEffectDefinition
    | CombatModifierEffect
    | MaxHpReductionEffectDefinition
    | AttachmentEffectDefinition,
    Field(discriminator="kind"),
]

__all__ = [
    "AttachmentEffectDefinition",
    "AttackEffectDefinition",
    "CombatModifierEffect",
    "ConditionEffectDefinition",
    "DamageEffectDefinition",
    "DiceSpec",
    "GrappleEffectDefinition",
    "HitModifierEffect",
    "MaxHpReductionEffectDefinition",
    "ProneEffectDefinition",
    "SaveFailureEffectDefinition",
]
