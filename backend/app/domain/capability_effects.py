from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.combatants import DamageType
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.size import CreatureSize
from app.domain.zero_hp_effects import ZeroHpSaveDamageRider


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


class SaveDamageEffectDefinition(BaseModel):
    kind: Literal["save_damage"] = "save_damage"
    source: str
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    dice: DiceSpec
    damage_type: DamageType
    success_damage: Literal["none", "half"] = "half"
    zero_hp_rider: ZeroHpSaveDamageRider | None = None


class SaveMaximumHpReductionEffectDefinition(BaseModel):
    kind: Literal["save_max_hp_reduction"] = "save_max_hp_reduction"
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    reduction: Literal["damage_taken"] = "damage_taken"
    zero_max_hp_kills: bool = False


class ProneEffectDefinition(BaseModel):
    kind: Literal["prone"] = "prone"
    max_target_size: CreatureSize | None = None


class SaveConditionEffectDefinition(BaseModel):
    kind: Literal["save_condition"] = "save_condition"
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    condition: ConditionName
    max_target_size: CreatureSize | None = None
    duration_rounds: int | None = Field(default=None, ge=1, le=100800)
    repeat_save_timing: ConditionTiming | None = None
    repeat_save_failure_condition: ConditionName | None = None
    failure_push_ft: int = Field(default=0, ge=0)
    excluded_creature_types: list[str] = Field(default_factory=list)
    excluded_creature_subtypes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_condition_lifecycle(self) -> "SaveConditionEffectDefinition":
        if (
            self.repeat_save_timing is not None
            and self.duration_rounds is None
            and self.repeat_save_failure_condition is None
        ):
            raise ValueError(
                "Save-condition repeat saves require a duration or a failure escalation condition."
            )
        if self.repeat_save_failure_condition is not None and self.repeat_save_timing is None:
            raise ValueError("Failure escalation requires a repeat-save timing.")
        return self


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
    DamageEffectDefinition | SaveDamageEffectDefinition | SaveMaximumHpReductionEffectDefinition | ProneEffectDefinition | SaveConditionEffectDefinition |
    GrappleEffectDefinition | ConditionEffectDefinition | HitModifierEffect,
    Field(discriminator="kind"),
]
