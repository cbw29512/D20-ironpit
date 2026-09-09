from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, Field

from app.domain.actions import ConditionName
from app.domain.capability_effects import AttackEffectDefinition
from app.domain.size import CreatureSize


class HealingEffectIR(BaseModel):
    kind: Literal["healing"] = "healing"
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    bonus: int = Field(default=0, ge=0)


class ConditionRemovalEffectIR(BaseModel):
    kind: Literal["condition_removal"] = "condition_removal"
    removable_conditions: list[ConditionName] = Field(min_length=1)
    max_conditions_per_use: int = Field(default=1, ge=1, le=16)
    expends_spell_slot: bool = False


class ArmorClassModifierEffectIR(BaseModel):
    kind: Literal["armor_class_modifier"] = "armor_class_modifier"
    amount: int = Field(ge=1, le=20)
    applies_to_triggering_attack: bool = False


class AttackRedirectEffectIR(BaseModel):
    kind: Literal["attack_redirect"] = "attack_redirect"
    ally_range_ft: int = Field(ge=1, le=30)
    ally_max_size: CreatureSize
    swap_positions: bool = False
    ally_becomes_target: bool = False


CombatEffectIR: TypeAlias = (
    AttackEffectDefinition
    | HealingEffectIR
    | ConditionRemovalEffectIR
    | ArmorClassModifierEffectIR
    | AttackRedirectEffectIR
)
