from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class DamageType(StrEnum):
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"


class WeaponAttackKind(StrEnum):
    MELEE = "melee"
    RANGED = "ranged"


class WeaponProperty(StrEnum):
    AMMUNITION = "ammunition"
    FINESSE = "finesse"
    LIGHT = "light"
    TWO_HANDED = "two-handed"
    VERSATILE = "versatile"


class AttackRollEffectKind(StrEnum):
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


class AttackRollEffect(BaseModel):
    id: str
    source_actor_id: str
    kind: AttackRollEffectKind
    target_actor_id: str | None = None
    consume_on_attack: bool = True
    expires_at_start_of_source_turn: bool = True
    source_turns_remaining: int | None = Field(default=None, ge=1)


class ConditionalDamage(BaseModel):
    trigger: Literal["attack_advantage"]
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
    properties: list[WeaponProperty] = Field(default_factory=list)
    mastery_property: str | None = None


class WeaponAttack(BaseModel):
    id: str
    weapon: Weapon
    attack_bonus: int
    ability_damage_modifier: int = 0
    damage_bonus: int = 0
    conditional_damage: list[ConditionalDamage] = Field(default_factory=list)


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
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    initiative_bonus: int
    weapon_attack: WeaponAttack
    alternate_weapon_attacks: list[WeaponAttack] = Field(default_factory=list)
    fighting_style: str | None = None
    weapon_masteries: list[str] = Field(default_factory=list)
    bonus_action_features: list[str] = Field(default_factory=list)
    visual: VisualLoadout
    resources: list[ResourceDefinition] = Field(default_factory=list)
    source: str


class DemoRoster(BaseModel):
    fighter: CombatantTemplate
    monster: CombatantTemplate


class CombatantState(BaseModel):
    template: CombatantTemplate
    current_hp: int
    initiative_roll: int | None = None
    initiative_total: int | None = None
    is_alive: bool = True
    action_available: bool = True
    bonus_action_available: bool = True
    reaction_available: bool = True
    movement_remaining_ft: int = Field(default=0, ge=0)
    disengaged: bool = False
    light_extra_attack_used: bool = False
    resources: list[ResourceState] = Field(default_factory=list)
    attack_roll_effects: list[AttackRollEffect] = Field(default_factory=list)


class BattlefieldState(BaseModel):
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)
