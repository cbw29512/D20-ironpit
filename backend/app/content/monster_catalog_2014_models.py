from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.actions import ConditionName
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType


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
    reach_ft: int = Field(default=5, ge=0)
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)


class CatalogMonster2014(BaseModel):
    id: str
    name: str
    ruleset: Literal["2014"]
    size: CreatureSize
    creature_type: str
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
    skills: dict[str, int] = Field(default_factory=dict)
    senses: str | None = None
    languages: str | None = None
    damage_resistances: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    condition_immunities: list[ConditionName] = Field(default_factory=list)
    unsupported_defense_text: list[str] = Field(default_factory=list)
    challenge_rating: str | None = None
    attacks: list[CatalogAttack2014] = Field(default_factory=list)
    action_names: list[str] = Field(default_factory=list)
    trait_names: list[str] = Field(default_factory=list)
    reaction_names: list[str] = Field(default_factory=list)
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
