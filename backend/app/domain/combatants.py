from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.abilities import AbilityKind
from app.domain.conditions import ConditionKind
from app.domain.damage import DamageType
from app.domain.resources import ResourceDefinition, ResourceState
from app.domain.visibility import ActorVisibilityState


class WeaponAttackKind(StrEnum):
    MELEE = "melee"
    RANGED = "ranged"


class WeaponProperty(StrEnum):
    AMMUNITION = "ammunition"
    FINESSE = "finesse"
    LIGHT = "light"
    THROWN = "thrown"
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
    open_tactic_eligible: bool = True


class VisualLoadout(BaseModel):
    armor: str
    main_hand: str
    off_hand: str | None = None
    body_style: str = "humanoid"


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
    proficiency_bonus: int = Field(default=2, ge=0)
    ability_modifiers: dict[AbilityKind, int] = Field(default_factory=dict)
    saving_throw_proficiencies: set[AbilityKind] = Field(default_factory=set)
    weapon_attack: WeaponAttack
    alternate_weapon_attacks: list[WeaponAttack] = Field(default_factory=list)
    fighting_style: str | None = None
    weapon_masteries: list[str] = Field(default_factory=list)
    bonus_action_features: list[str] = Field(default_factory=list)
    sneak_attack_dice_count: int = Field(default=0, ge=0, le=10)
    skill_bonuses: dict[str, int] = Field(default_factory=dict)
    passive_perception: int = Field(default=10, ge=0)
    visual: VisualLoadout
    resources: list[ResourceDefinition] = Field(default_factory=list)
    damage_resistances: set[DamageType] = Field(default_factory=set)
    damage_immunities: set[DamageType] = Field(default_factory=set)
    damage_vulnerabilities: set[DamageType] = Field(default_factory=set)
    wearing_heavy_armor: bool = False
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
    turn_active: bool = False
    action_available: bool = True
    bonus_action_available: bool = True
    reaction_available: bool = True
    movement_remaining_ft: int = Field(default=0, ge=0)
    disengaged: bool = False
    dodging: bool = False
    light_extra_attack_used: bool = False
    hidden: bool = False
    hidden_dc: int | None = Field(default=None, ge=0)
    conditions: set[ConditionKind] = Field(default_factory=set)
    once_per_turn_features_used: set[str] = Field(default_factory=set)
    resources: list[ResourceState] = Field(default_factory=list)
    attack_roll_effects: list[AttackRollEffect] = Field(default_factory=list)
    temporary_damage_resistances: set[DamageType] = Field(default_factory=set)
    raging: bool = False
    rage_extension_required: bool = False
    rage_extended_this_turn: bool = False


class BattlefieldState(BaseModel):
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)
    visibility_by_actor: dict[str, ActorVisibilityState] = Field(default_factory=dict)
