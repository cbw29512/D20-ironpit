from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming, GrapplePeriodicDamage
from app.domain.attachment_sources import OnHitAttachment
from app.domain.combatants import DamageType
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.breakable_restraints import BreakableObjectSpec
from app.domain.size import CreatureSize
from app.domain.zero_hp_effects import ZeroHpSaveDamageRider
from app.domain.save_condition_effects import (
    OngoingHpLossEffectDefinition,
    SaveConditionEffectDefinition,
    SavePersistentEffectDefinition,
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
    trigger: Literal["on_hit", "attack_advantage", "attacker_bloodied", "target_bloodied", "round1_initiative_lead", "attacker_active_effect"] = "on_hit"
    mode: Literal["add", "replace_weapon"] = "add"
    required_effect_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_conditional_effect(self) -> "DamageEffectDefinition":
        if (self.trigger == "attacker_active_effect") != (self.required_effect_id is not None):
            raise ValueError("Active-effect damage must declare one required combat effect ID.")
        return self


class SaveDamageEffectDefinition(BaseModel):
    kind: Literal["save_damage"] = "save_damage"
    source: str
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    dice: DiceSpec
    damage_type: DamageType
    success_damage: Literal["none", "half"] = "half"
    zero_hp_rider: ZeroHpSaveDamageRider | None = None
    failed_save_condition: SaveConditionEffectDefinition | None = None


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
    max_active_grapples: int | None = Field(default=None, ge=1, le=20)
    # Declarative object durability for a Grapple's external appendage/snare.
    breakable_object: BreakableObjectSpec | None = None
    # Applies only to checks and saves while the corresponding Grapple exists.
    check_save_disadvantage_abilities: list[AbilityName] = Field(default_factory=list)
    # Legacy max_target_size limits the entire save. Only a source with a
    # separately printed damage-versus-grapple size rule sets this true.
    size_only_applies_to_grapple: bool = Field(
        default=False, exclude_if=lambda value: not value,
    )
    # A source-defined slot cost makes a Large creature occupy two of two
    # capacity slots without inventing creature/ability-name runtime logic.
    large_target_slot_cost: int = Field(
        default=1, ge=1, le=20, exclude_if=lambda value: value == 1,
    )
    prevents_breathing: bool = Field(default=False, exclude_if=lambda value: not value)
    breathing_exempt_medium: Literal["water"] | None = None
    periodic_damage: GrapplePeriodicDamage | None = None

    @model_validator(mode="after")
    def validate_capacity(self) -> "GrappleEffectDefinition":
        if self.breathing_exempt_medium is not None and not self.prevents_breathing:
            raise ValueError("A breathing-medium exception requires breathing prevention.")
        if self.large_target_slot_cost > 1 and self.max_active_grapples is None:
            raise ValueError("Weighted grapple slots require a total capacity.")
        return self


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
    escape_check_ability: AbilityName | None = None
    escape_check_dc: int | None = Field(default=None, ge=1, le=40)
    breakable_object: BreakableObjectSpec | None = None


class AttachmentEffectDefinition(OnHitAttachment):
    kind: Literal["attachment"] = "attachment"


AttackEffectDefinition = Annotated[
    DamageEffectDefinition | SaveDamageEffectDefinition | AbilityScoreReductionEffectDefinition | SaveMaximumHpReductionEffectDefinition | ContestedMovementEffectDefinition | ProneEffectDefinition | SaveConditionEffectDefinition |
    GrappleEffectDefinition | ConditionEffectDefinition | AttachmentEffectDefinition | OngoingHpLossEffectDefinition |
    SavePersistentEffectDefinition | HitModifierEffect,
    Field(discriminator="kind"),
]
