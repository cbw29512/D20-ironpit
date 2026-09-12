from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.actions import AbilityName, ConditionName, HitControlEffect, SavingThrowAction
from app.domain.charge_profiles import ChargeProfileDefinition
from app.domain.on_hit_saves import OnHitSaveEffect
from app.domain.size import CreatureSize
from app.domain.weapons import ConditionalDamage, DamageType


class CatalogDamage2014(BaseModel):
    average: int = Field(ge=0)
    dice_count: int = Field(ge=0, le=40)
    dice_size: int = Field(ge=2, le=100)
    bonus: int = 0
    type: DamageType


class CatalogAttack2014(BaseModel):
    id: str
    name: str
    kind: Literal["melee", "ranged"]
    attack_bonus: int
    damage: CatalogDamage2014
    conditional_damage: list[ConditionalDamage] = Field(default_factory=list)
    on_hit_damage: list[CatalogDamage2014] = Field(default_factory=list)
    on_hit_save_effect: OnHitSaveEffect | None = None
    control_effect: HitControlEffect | None = None
    forbid_target_grappled_by_self: bool = False
    charge_profile: ChargeProfileDefinition | None = None
    reach_ft: int = Field(default=5, ge=0)
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)
    source_complete: bool = True
    unsupported_text: str | None = None


class CatalogInnateSpell2014(BaseModel):
    id: str
    name: str
    usage: Literal["at_will", "per_day"]
    uses_per_day: int | None = Field(default=None, ge=1, le=9)
    shared_pool: bool = False
    qualifier: str | None = None


class CatalogInnateSpellcasting2014(BaseModel):
    ability: AbilityName
    save_dc: int | None = Field(default=None, ge=1, le=40)
    attack_bonus: int | None = Field(default=None, ge=-10, le=30)
    spells: list[CatalogInnateSpell2014] = Field(default_factory=list)
    source_complete: bool = True
    unsupported_text: str | None = None


class CatalogPreparedSpell2014(BaseModel):
    id: str
    name: str
    level: int = Field(ge=0, le=9)


class CatalogSpellcasting2014(BaseModel):
    caster_level: int = Field(ge=1, le=20)
    ability: AbilityName
    save_dc: int | None = Field(default=None, ge=1, le=40)
    attack_bonus: int | None = Field(default=None, ge=-10, le=30)
    slots: dict[str, int] = Field(default_factory=dict)
    spells: list[CatalogPreparedSpell2014] = Field(default_factory=list)
    source_complete: bool = True
    unsupported_text: str | None = None


class CatalogMonster2014(BaseModel):
    id: str
    name: str
    ruleset: Literal["2014"]
    size: CreatureSize
    creature_type: str
    creature_type_text: str | None = None
    creature_subtypes: list[str] = Field(default_factory=list)
    alignment: str | None = None
    armor_class: int = Field(ge=1)
    armor_class_text: str | None = None
    max_hp: int = Field(ge=1)
    hit_points_text: str | None = None
    hit_dice: str | None = None
    speed: dict[str, int]
    speed_text: str | None = None
    abilities: dict[str, int]
    saving_throws: dict[str, int] = Field(default_factory=dict)
    saving_throws_text: str | None = None
    skills: dict[str, int] = Field(default_factory=dict)
    skills_text: str | None = None
    senses: str | None = None
    languages: str | None = None
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_resistances_text: str | None = None
    damage_immunities: list[DamageType] = Field(default_factory=list)
    damage_immunities_text: str | None = None
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_vulnerabilities_text: str | None = None
    condition_immunities: list[ConditionName] = Field(default_factory=list)
    condition_immunities_text: str | None = None
    unsupported_defense_text: list[str] = Field(default_factory=list)
    challenge_rating: str | None = None
    challenge_text: str | None = None
    attacks: list[CatalogAttack2014] = Field(default_factory=list)
    saving_throw_actions: list[SavingThrowAction] = Field(default_factory=list)
    innate_spellcasting: CatalogInnateSpellcasting2014 | None = None
    spellcasting: CatalogSpellcasting2014 | None = None
    multiattack_slots: list[list[str]] = Field(default_factory=list)
    action_recharges: dict[str, int] = Field(default_factory=dict)
    rest_recharge_action_ids: list[str] = Field(default_factory=list)
    action_names: list[str] = Field(default_factory=list)
    trait_names: list[str] = Field(default_factory=list)
    reaction_names: list[str] = Field(default_factory=list)
    parry_ac_bonus: int | None = Field(default=None, ge=1, le=20)
    legendary_action_names: list[str] = Field(default_factory=list)
    source_traits: str | None = None
    source_actions: str | None = None
    source_reactions: str | None = None
    source_legendary_actions: str | None = None
    image_url: str | None = None

    @field_validator("size", mode="before")
    @classmethod
    def normalize_size(cls, value: object) -> object:
        return value.lower() if isinstance(value, str) else value
