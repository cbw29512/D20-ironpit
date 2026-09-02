from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.class_loadouts import MeleeLoadoutKind

AbilityName = Literal[
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]
EquipmentOption = Literal["package", "gold"]


class AbilityScores(BaseModel):
    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)

    def score(self, ability: AbilityName) -> int:
        return int(getattr(self, ability))

    def modifier(self, ability: AbilityName) -> int:
        return (self.score(ability) - 10) // 2


class AbilityIncrease(BaseModel):
    ability: AbilityName
    amount: int = Field(ge=1, le=2)


class FeatureAudit(BaseModel):
    feature_id: str
    feature_name: str
    source_reference: str
    category: Literal["class", "subclass", "species", "background", "feat", "equipment"]
    combat_relevant: bool
    automated: bool
    runtime_attack_weapon_id: str | None = None
    notes: str | None = None


class CharacterBuildProfile(BaseModel):
    id: str
    template_id: str
    character_name: str
    class_id: str
    class_name: str
    level: int = Field(ge=1, le=20)
    subclass_id: str | None = None
    subclass_name: str | None = None
    build_id: str | None = None
    species_id: str
    species_name: str
    background_id: str
    background_name: str
    origin_feat_id: str
    origin_feat_name: str
    base_ability_scores: AbilityScores
    background_allowed_abilities: list[AbilityName] = Field(min_length=3, max_length=3)
    background_increases: list[AbilityIncrease] = Field(min_length=2, max_length=3)
    advancement_increases: list[AbilityIncrease] = Field(default_factory=list)
    final_ability_scores: AbilityScores
    class_equipment_option: EquipmentOption
    class_equipment: list[str] = Field(min_length=1)
    background_equipment_option: EquipmentOption
    background_equipment: list[str] = Field(min_length=1)
    skill_proficiencies: list[str] = Field(default_factory=list)
    weapon_masteries: list[str] = Field(default_factory=list)
    fighting_style: str | None = None
    combat_loadout_kind: MeleeLoadoutKind | None = None
    feature_audits: list[FeatureAudit] = Field(min_length=1)
    source_references: list[str] = Field(min_length=1)
