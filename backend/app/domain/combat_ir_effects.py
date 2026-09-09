from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, Field

from app.domain.actions import ConditionName
from app.domain.capability_effects import AttackEffectDefinition


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


CombatEffectIR: TypeAlias = AttackEffectDefinition | HealingEffectIR | ConditionRemovalEffectIR
