from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.ability_reduction import AbilityScoreReductionOnHit
from app.domain.actions import AbilityName, HitControlEffect
from app.domain.charge import ChargeProfile
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.size import CreatureSize


class DamageType(StrEnum):
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"


class WeaponAttackKind(StrEnum):
    MELEE = "melee"
    RANGED = "ranged"
    MELEE_OR_RANGED = "melee_or_ranged"


class ConditionalDamage(BaseModel):
    trigger: Literal["attack_advantage", "attacker_bloodied", "target_bloodied"]
    mode: Literal["add", "replace_weapon"] = "add"
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType


class ConditionalAttackAdvantage(BaseModel):
    trigger: Literal["target_not_full_hp"]


class OnHitDamage(BaseModel):
    source: str
    dice_count: int = Field(ge=0, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType

    @model_validator(mode="after")
    def _fixed_damage_requires_positive_amount(self) -> "OnHitDamage":
        if self.dice_count == 0 and self.damage_bonus <= 0:
            raise ValueError("A zero-die on-hit damage rider requires a positive fixed damage amount.")
        return self


class MaxHpReductionOnHit(BaseModel):
    """Reduce maximum HP by applied attack damage, optionally from one damage type only."""

    damage_type: DamageType | None = None


class AttachmentOnHit(BaseModel):
    """Create a source-owned attachment relation after this attack hits."""

    periodic_damage_count: int = Field(ge=0, le=40)
    periodic_damage_size: int = Field(default=6, ge=2, le=100)
    periodic_damage_bonus: int = 0
    periodic_damage_type: DamageType
    forbids_source_attack_ids: list[str] = Field(default_factory=list)
    detachable_by_source_movement_ft: int | None = Field(default=None, ge=5, le=120)
    detachable_by_target_action: bool = True
    detachable_by_adjacent_action: bool = True


class Weapon(BaseModel):
    id: str
    name: str
    attack_kind: WeaponAttackKind
    dice_count: int = Field(ge=0, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    animation: str
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


class WeaponAttack(BaseModel):
    id: str
    weapon: Weapon
    attack_bonus: int
    damage_bonus: int
    damage_die_minimum: int | None = Field(default=None, ge=2, le=100)
    attack_ability: AbilityName | None = None
    attack_ability_modifier: int | None = None
    fixed_damage: int | None = Field(default=None, ge=0)
    conditional_damage: list[ConditionalDamage] = Field(default_factory=list)
    conditional_attack_advantage: list[ConditionalAttackAdvantage] = Field(default_factory=list)
    on_hit_damage: list[OnHitDamage] = Field(default_factory=list)
    on_hit_modifier_effects: list[HitModifierEffect] = Field(default_factory=list)
    max_hp_reduction_on_hit: MaxHpReductionOnHit | None = None
    ability_score_reduction_on_hit: AbilityScoreReductionOnHit | None = None
    attachment_on_hit: AttachmentOnHit | None = None
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    rage_eligible: bool = False
    sneak_attack_eligible: bool = False
    knocks_prone_max_size: CreatureSize | None = None
    control_effect: HitControlEffect | None = None
    charge_profile: ChargeProfile | None = None
    push_target_away_ft: int = Field(default=0, ge=0, le=120)
    push_target_max_size: CreatureSize | None = None
    pull_target_toward_ft: int = Field(default=0, ge=0, le=120)
    pull_target_max_size: CreatureSize | None = None
    forbid_target_grappled_by_self: bool = False

    @model_validator(mode="after")
    def validate_forced_movement(self) -> "WeaponAttack":
        if self.push_target_away_ft and self.pull_target_toward_ft:
            raise ValueError("An attack cannot both push and pull the same target on hit.")
        if self.push_target_max_size is not None and self.push_target_away_ft == 0:
            raise ValueError("Push target size requires a positive push distance.")
        if self.pull_target_max_size is not None and self.pull_target_toward_ft == 0:
            raise ValueError("Pull target size requires a positive pull distance.")
        if self.push_target_away_ft % 5 or self.pull_target_toward_ft % 5:
            raise ValueError("Forced movement distance must use 5-foot increments.")
        return self
