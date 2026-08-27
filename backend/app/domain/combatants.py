from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.conditions import ConditionState, ConditionType
from app.domain.effects import AttackEffect, SizeCategory


class DamageType(StrEnum):
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"
    POISON = "poison"
    RADIANT = "radiant"


class WeaponAttackKind(StrEnum):
    MELEE = "melee"
    RANGED = "ranged"
    THROWN = "thrown"


class ConditionalDamage(BaseModel):
    trigger: Literal["always", "attack_advantage"]
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType


class Weapon(BaseModel):
    id: str
    name: str
    attack_kind: WeaponAttackKind
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    animation: str
    reach_ft: int = Field(default=5, ge=0)
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)
    projectile: str | None = None
    mastery_property: str | None = None


class DamageDiceOverride(BaseModel):
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)


class WeaponAttack(BaseModel):
    id: str
    weapon: Weapon
    attack_bonus: int
    damage_bonus: int
    damage_dice: DamageDiceOverride | None = None
    conditional_damage: list[ConditionalDamage] = Field(default_factory=list)
    on_hit_effects: list[AttackEffect] = Field(default_factory=list)


class VisualLoadout(BaseModel):
    armor: str
    main_hand: str
    off_hand: str | None = None
    body_style: str = "humanoid"


class ResourceDefinition(BaseModel):
    id: str
    name: str
    max_uses: int = Field(ge=0)


class ResourceState(BaseModel):
    id: str
    name: str
    current_uses: int = Field(ge=0)
    max_uses: int = Field(ge=0)


class CombatantTemplate(BaseModel):
    id: str
    name: str
    archetype: str
    level: int | None = Field(default=None, ge=1, le=20)
    challenge_rating: str | None = None
    kind: Literal["character", "monster"]
    size: SizeCategory = SizeCategory.MEDIUM
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    initiative_bonus: int
    attacks_per_action: int = Field(default=1, ge=1, le=10)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)
    condition_immunities: list[ConditionType] = Field(default_factory=list)
    weapon_attack: WeaponAttack
    alternate_weapon_attacks: list[WeaponAttack] = Field(default_factory=list)
    fighting_style: str | None = None
    weapon_masteries: list[str] = Field(default_factory=list)
    visual: VisualLoadout
    resources: list[ResourceDefinition] = Field(default_factory=list)
    source: str


class DemoRoster(BaseModel):
    fighter: CombatantTemplate
    monster: CombatantTemplate


class CombatantState(BaseModel):
    template: CombatantTemplate
    instance_id: str = Field(min_length=1)
    current_hp: int
    initiative_roll: int | None = None
    initiative_total: int | None = None
    is_alive: bool = True
    action_available: bool = True
    bonus_action_available: bool = True
    action_surge_used_this_turn: bool = False
    movement_remaining_ft: int = Field(default=0, ge=0)
    resources: list[ResourceState] = Field(default_factory=list)
    conditions: list[ConditionState] = Field(default_factory=list)


class BattlefieldState(BaseModel):
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)
