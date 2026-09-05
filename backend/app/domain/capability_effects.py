from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.combatants import DamageType
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.size import CreatureSize


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
    kind: Literal["max-hp-reduction"] = "max-hp-reduction"
    damage_type: DamageType | None = None


class ProneEffectDefinition(BaseModel):
    kind: Literal["prone"] = "prone"
    max_target_size: CreatureSize | None = None


class GrappleEffectDefinition(BaseModel):
    kind: Literal["grapple"] = "grapple"
    escape_dc: int = Field(ge=1, le=40)
    max_target_size: CreatureSize | None = None
    restrains: bool = False


class ConditionEffectDefinition(BaseModel):
    kind: Literal["condition"] = "condition"
    condition: ConditionName
    max_target_size: CreatureSize | None = None
    expires_at_start_of_source_turn: bool = False
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    allowed_removal_action_ids: list[str] = Field(default_factory=list)


AttackEffectDefinition = Annotated[
    DamageEffectDefinition | MaxHpReductionEffectDefinition | ProneEffectDefinition | GrappleEffectDefinition | ConditionEffectDefinition | HitModifierEffect,
    Field(discriminator="kind"),
]
