from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import (
    AttackActionDefinition,
    ConditionName,
    ConditionRemovalAction,
    HealingAction,
    HitControlEffect,
    SavingThrowAction,
)
from app.domain.movement import MovementModes
from app.domain.size import CreatureSize
from app.domain.spells import DefensiveSpellAction, SpellSaveAction
from app.domain.traits import CombatTrait


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


class ConditionalDamage(BaseModel):
    trigger: Literal["attack_advantage"]
    dice_count: int = Field(ge=1, le=20)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType


class OnHitDamage(BaseModel):
    source: str
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType


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


class WeaponAttack(BaseModel):
    id: str
    weapon: Weapon
    attack_bonus: int
    damage_bonus: int
    fixed_damage: int | None = Field(default=None, ge=0)
    conditional_damage: list[ConditionalDamage] = Field(default_factory=list)
    on_hit_damage: list[OnHitDamage] = Field(default_factory=list)
    rage_eligible: bool = False
    knocks_prone_max_size: CreatureSize | None = None
    control_effect: HitControlEffect | None = None
    forbid_target_grappled_by_self: bool = False


class VisualLoadout(BaseModel):
    armor: str
    main_hand: str
    off_hand: str | None = None
    body_style: str = "humanoid"


class ResourceDefinition(BaseModel):
    id: str
    name: str
    max_uses: int = Field(ge=0)


class CombatantTemplate(BaseModel):
    id: str
    name: str
    archetype: str
    level: int | None = Field(default=None, ge=1, le=20)
    challenge_rating: str | None = None
    kind: Literal["character", "monster"]
    size: CreatureSize = CreatureSize.MEDIUM
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    movement_modes: MovementModes
    initiative_bonus: int
    weapon_attack: WeaponAttack
    alternate_weapon_attacks: list[WeaponAttack] = Field(default_factory=list)
    attack_action: AttackActionDefinition | None = None
    saving_throw_actions: list[SavingThrowAction] = Field(default_factory=list)
    spell_save_actions: list[SpellSaveAction] = Field(default_factory=list)
    defensive_spell_actions: list[DefensiveSpellAction] = Field(default_factory=list)
    healing_actions: list[HealingAction] = Field(default_factory=list)
    condition_removal_actions: list[ConditionRemovalAction] = Field(default_factory=list)
    saving_throw_bonuses: dict[str, int] = Field(default_factory=dict)
    skill_bonuses: dict[str, int] = Field(default_factory=dict)
    combat_traits: list[CombatTrait] = Field(default_factory=list)
    source_trait_names: list[str] = Field(default_factory=list)
    fighting_style: str | None = None
    weapon_masteries: list[str] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)
    condition_immunities: list[ConditionName] = Field(default_factory=list)
    wearing_heavy_armor: bool = False
    rage_damage_bonus: int = Field(default=0, ge=0, le=10)
    visual: VisualLoadout
    resources: list[ResourceDefinition] = Field(default_factory=list)
    source: str

    @model_validator(mode="before")
    @classmethod
    def _default_movement_modes(cls, values: object) -> object:
        if isinstance(values, dict) and "movement_modes" not in values and "speed_ft" in values:
            return {**values, "movement_modes": {"walk_ft": values["speed_ft"]}}
        return values
