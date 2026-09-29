from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.character_builds import AbilityName
from app.domain.damage_sources import DamageSourceQualifier
from app.domain.d20_outcome_adjustments import ResourceBackedD20OutcomeAdjustment
from app.domain.weapons_base import DamageType


class AbilityCheckMinimum(BaseModel):
    """Declarative floor for one ability-check family; resolution remains name-agnostic."""

    source_id: str
    ability: AbilityName
    minimum_source: Literal["ability_score"] = "ability_score"


class SavingThrowMinimum(BaseModel):
    """Declarative floor for one saving-throw family; resolution remains name-agnostic."""

    source_id: str
    ability: AbilityName
    minimum_source: Literal["ability_score"] = "ability_score"


class DamageResistanceBypassGrant(BaseModel):
    """Source-owned permission for matching outgoing damage to ignore Resistance only."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    damage_types: list[DamageType] = Field(min_length=1)


class NaturalTwentyAttackDamageGrant(BaseModel):
    """Flat extra damage when the attack d20 itself is a natural 20."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    ability: AbilityName
    damage_type_source: Literal["attack"] = "attack"


class AbilityScaledDamageRider(BaseModel):
    """Damage dice count derived from one ability modifier."""

    source_id: str
    ability: AbilityName
    dice_size: int = Field(ge=2, le=100)
    damage_type: str


class SlotHealingSelfRider(BaseModel):
    """Heal the source after a slotted healing spell restores HP to another creature."""

    source_id: str
    flat_bonus: int = Field(default=0, ge=0)
    per_slot_level: int = Field(default=0, ge=0)


class EffectBoundSurvivalSave(BaseModel):
    """Immutable zero-HP replacement parameters; no class identity enters resolution."""

    source_id: str
    required_effect_id: str
    save_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"] = "constitution"
    initial_dc: int = Field(ge=1)
    dc_increment: int = Field(default=0, ge=0)
    replacement_hp: int = Field(ge=1)


class FirstRoundExtraTurnGrant(BaseModel):
    source_id: str
    source_name: str
    initiative_offset: int = Field(ge=-30, le=30)


class OpeningTargetingWard(BaseModel):
    source_id: str
    save_ability: AbilityName = "wisdom"
    save_dc: int = Field(ge=1, le=40)
    ends_on_owner_attack: bool = True


class SavingThrowProficiencyGrant(BaseModel):
    source_id: str
    abilities: list[AbilityName] = Field(min_length=1)


class FailedSaveRerollGrant(BaseModel):
    source_id: str
    source_name: str
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)


class FailedD20TestOverrideGrant(BaseModel):
    source_id: str
    source_name: str
    resource_id: str
    replacement_roll: int = Field(default=20, ge=1, le=20)
    test_kinds: list[Literal["attack", "saving_throw", "ability_check"]] = Field(min_length=1)


class ResourceBackedD20BonusDie(BaseModel):
    """Spend a declared resource when a matching failed d20 test can be improved."""

    source_id: str
    source_name: str
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)
    dice_count: int = Field(default=1, ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    test_kinds: list[Literal["attack", "saving_throw", "ability_check"]] = Field(min_length=1)


class DeferredSaveEffect(BaseModel):
    source_id: str
    source_name: str
    trigger_weapon_ids: list[str] = Field(min_length=1)
    resource_id: str
    resource_cost: int = Field(default=1, ge=1)
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    failure_sets_zero_hp: bool = False
    success_damage_dice_count: int = Field(default=0, ge=0, le=40)
    success_damage_dice_size: int = Field(default=10, ge=2, le=100)
    success_damage_type: str | None = None
    max_active_targets: int = Field(default=1, ge=1, le=20)


class SourceReducesHostileToZeroHpTemporaryHp(BaseModel):
    """Grant source-owned Temporary HP after this source reduces a hostile creature to 0 HP."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    ability: AbilityName
    flat_bonus: int = 0
    per_level: int = Field(default=0, ge=0)
    minimum: int = Field(default=1, ge=0)


class SourceDamageTemporaryHpGrant(BaseModel):
    """Grant source-owned Temporary HP after declared source actions deal actual damage."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    trigger_action_ids: list[str] = Field(min_length=1)
    ability: AbilityName
    ability_multiplier: int = Field(default=1, ge=1, le=10)
    flat_bonus: int = 0
    minimum: int = Field(default=0, ge=0)


class SelectableDamageResistance(BaseModel):
    """Choose one legal damage type at a preparation boundary and resist matching damage."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    allowed_damage_types: list[DamageType] = Field(min_length=1)
    forbidden_source_qualifiers: list[DamageSourceQualifier] = Field(default_factory=list)
    priority: int = 0


class ResourceBackedOnHitExile(BaseModel):
    """On a qualifying hit, spend a finite resource to remove the target until a source-relative return point."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1)
    expiry_timing: str = "source_turn_end"
    duration_rounds: int = Field(default=1, ge=1)
    return_damage_dice_count: int = Field(default=0, ge=0)
    return_damage_dice_size: int = Field(default=0, ge=0)
    return_damage_bonus: int = 0
    return_damage_type: DamageType | None = None
    return_damage_excluded_creature_types: list[str] = Field(default_factory=list)


class DelayedResourceRefill(BaseModel):
    """Automatically arm a source-owned timer when declared resources are below maximum."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_ids: list[str] = Field(min_length=1)
    use_resource_id: str = Field(min_length=1)
    use_resource_cost: int = Field(default=1, ge=1)
    delay_rounds: int = Field(ge=1)
