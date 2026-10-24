from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming, GrapplePeriodicDamage
from app.domain.combatants import DamageType
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.size import CreatureSize
from app.domain.zero_hp_effects import ZeroHpSaveDamageRider
from app.domain.save_condition_effects import OngoingHpLossEffectDefinition, SaveConditionEffectDefinition


class DiceSpec(BaseModel):
    count: int = Field(ge=0, le=40)
    size: int = Field(default=6, ge=2, le=100)
    bonus: int = 0


class DamageEffectDefinition(BaseModel):
    kind: Literal["damage"] = "damage"
    source: str
    dice: DiceSpec
    damage_type: DamageType
    trigger: Literal["on_hit", "attack_advantage", "attacker_bloodied", "target_bloodied", "round1_initiative_lead"] = "on_hit"
    mode: Literal["add", "replace_weapon"] = "add"


class SaveDamageEffectDefinition(BaseModel):
    kind: Literal["save_damage"] = "save_damage"
    source: str
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    dice: DiceSpec
    damage_type: DamageType
    success_damage: Literal["none", "half"] = "half"
    zero_hp_rider: ZeroHpSaveDamageRider | None = None


class AbilityScoreReductionEffectDefinition(BaseModel):
    """Source-declared, unsaved on-hit ability loss; templates remain immutable."""

    kind: Literal["ability_score_reduction"] = "ability_score_reduction"
    source: str = Field(min_length=1)
    ability: AbilityName
    dice: DiceSpec

    @model_validator(mode="after")
    def validate_roll(self) -> "AbilityScoreReductionEffectDefinition":
        if self.dice.count < 1 or self.dice.bonus:
            raise ValueError("Ability-score reduction needs dice without a flat bonus.")
        return self


class SaveMaximumHpReductionEffectDefinition(BaseModel):
    kind: Literal["save_max_hp_reduction"] = "save_max_hp_reduction"
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    reduction: Literal["damage_taken"] = "damage_taken"
    zero_max_hp_kills: bool = False


class ContestedMovementEffectDefinition(BaseModel):
    kind: Literal["contested_movement"] = "contested_movement"
    source_ability: AbilityName
    target_ability: AbilityName
    max_target_size: CreatureSize | None = None
    distance_ft: int = Field(ge=0)
    direction: Literal["toward_source", "away_from_source"]

    @model_validator(mode="after")
    def validate_grid_distance(self) -> "ContestedMovementEffectDefinition":
        if self.distance_ft % 5:
            raise ValueError("Contested forced movement must use 5-foot grid increments.")
        return self


class ProneEffectDefinition(BaseModel):
    kind: Literal["prone"] = "prone"
    max_target_size: CreatureSize | None = None



class GrappleEffectDefinition(BaseModel):
    kind: Literal["grapple"] = "grapple"
    escape_dc: int = Field(ge=1, le=40)
    max_target_size: CreatureSize | None = None
    restrains: bool = False
    requires_source_free: bool = False
    periodic_damage: GrapplePeriodicDamage | None = None


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
    DamageEffectDefinition | SaveDamageEffectDefinition | AbilityScoreReductionEffectDefinition | SaveMaximumHpReductionEffectDefinition | ContestedMovementEffectDefinition | ProneEffectDefinition | SaveConditionEffectDefinition |
    GrappleEffectDefinition | ConditionEffectDefinition | OngoingHpLossEffectDefinition | HitModifierEffect,
    Field(discriminator="kind"),
]
