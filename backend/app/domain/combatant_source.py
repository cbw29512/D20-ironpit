from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


AbilityName = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


class AbilityScoreDelta(BaseModel):
    strength: int | None = None
    dexterity: int | None = None
    constitution: int | None = None
    intelligence: int | None = None
    wisdom: int | None = None
    charisma: int | None = None


class AbilityScoresSource(BaseModel):
    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)


class HeroLevelDelta(BaseModel):
    """Class-only delta. Character stats, species, and loadout do not belong here."""

    level: int = Field(ge=1, le=20)
    proficiency_bonus: int | None = Field(default=None, ge=2, le=6)
    attack_count: int | None = Field(default=None, ge=1)
    unarmed_dice_size: int | None = Field(default=None, ge=4, le=12)
    resources: dict[str, int] = Field(default_factory=dict)
    capabilities_added: list[str] = Field(default_factory=list)
    capabilities_removed: list[str] = Field(default_factory=list)
    arena_ignored: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_level_one_foundation(self) -> "HeroLevelDelta":
        if self.level == 1 and (self.proficiency_bonus is None or self.attack_count is None):
            raise ValueError("Level 1 class row must define proficiency_bonus and attack_count.")
        return self


class HeroProgressionSource(BaseModel):
    schema_version: int = 1
    edition: Literal["2014", "2024"]
    class_id: str
    source: str
    hit_die: int = Field(ge=4, le=12)
    emit_attack_action_at_one: bool = False
    levels: list[HeroLevelDelta] = Field(min_length=1)

    @model_validator(mode="after")
    def contiguous_unique_levels(self) -> "HeroProgressionSource":
        actual = [row.level for row in self.levels]
        expected = list(range(1, max(actual) + 1))
        if actual != expected:
            raise ValueError(
                f"Progression levels must be ordered and contiguous: expected {expected}, got {actual}."
            )
        return self


class SubclassLevelDelta(BaseModel):
    capabilities_added: list[str] = Field(default_factory=list)
    capabilities_removed: list[str] = Field(default_factory=list)
    arena_ignored: list[str] = Field(default_factory=list)


class SubclassProgressionSource(BaseModel):
    schema_version: int = 1
    edition: Literal["2014", "2024"]
    class_id: str
    subclass_id: str
    deltas: dict[int, SubclassLevelDelta] = Field(default_factory=dict)


class SpeciesSource(BaseModel):
    schema_version: int = 1
    edition: Literal["2014", "2024"]
    id: str
    speed_ft: int = Field(ge=0)
    capabilities_added: list[str] = Field(default_factory=list)
    resources: dict[str, int] = Field(default_factory=dict)
    resource_equals_proficiency: list[str] = Field(default_factory=list)


class HeroIdentitySource(BaseModel):
    id: str
    name: str
    class_id: str
    subclass_id: str
    build_id: str
    species: str
    background: str
    track_id: str
    level_range: tuple[int, int]

    @model_validator(mode="after")
    def valid_level_range(self) -> "HeroIdentitySource":
        low, high = self.level_range
        if not 1 <= low <= high <= 20:
            raise ValueError("Hero level_range must stay within 1..20.")
        return self


class HeroCatalogSource(BaseModel):
    schema_version: int = 1
    edition: Literal["2014", "2024"]
    heroes: list[HeroIdentitySource]


class HeroTrackSource(BaseModel):
    """One persistent character: scores, ASIs, canonical HP, origin feats, mastery picks."""

    schema_version: int = 1
    edition: Literal["2014", "2024"]
    id: str
    hero_id: str
    class_id: str
    subclass_id: str
    species_id: str
    build_id: str
    origin_capabilities: list[str] = Field(default_factory=list)
    ability_scores: AbilityScoresSource
    ability_score_improvements: dict[int, AbilityScoreDelta] = Field(default_factory=dict)
    hp_by_level: list[int] = Field(min_length=1)
    ac_by_level: list[int] = Field(default_factory=list)
    speed_by_level: list[int] = Field(default_factory=list)
    rage_damage_bonus_by_level: list[int] = Field(default_factory=list)
    weapon_masteries_by_level: dict[int, list[str]] = Field(default_factory=dict)
    fighting_styles_by_level: dict[int, list[str]] = Field(default_factory=dict)
    expertise_by_level: dict[int, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_hp_and_asis(self) -> "HeroTrackSource":
        if any(hp < 1 for hp in self.hp_by_level):
            raise ValueError("hp_by_level values must be >= 1.")
        for level in self.ability_score_improvements:
            if not 2 <= int(level) <= 20:
                raise ValueError(f"ASI level {level} must be in 2..20.")
        for level in self.weapon_masteries_by_level:
            if not 1 <= int(level) <= 20:
                raise ValueError(f"Weapon mastery level {level} must be in 1..20.")
        for level in self.expertise_by_level:
            if not 1 <= int(level) <= 20:
                raise ValueError(f"Expertise level {level} must be in 1..20.")
        return self


class HeroSkillSource(BaseModel):
    id: str
    ability: AbilityName
    proficient: bool = True


class HeroAttackSource(BaseModel):
    id: str
    name: str
    weapon_id: str
    attack_kind: Literal["melee", "ranged"]
    ability: AbilityName
    dice_count: int = Field(ge=1)
    dice_size: int = Field(ge=2)
    damage_type: str
    reach_ft: int = Field(default=5, ge=0)
    normal_range_ft: int | None = Field(default=None, ge=1)
    long_range_ft: int | None = Field(default=None, ge=1)
    animation: str
    mastery_property: str | None = None
    heavy: bool = False
    two_handed: bool = False


class HeroBuildSource(BaseModel):
    schema_version: int = 1
    edition: Literal["2014", "2024"]
    id: str
    class_id: str
    armor_class: int = Field(ge=1)
    speed_ft: int = Field(ge=0)
    save_proficiencies: list[AbilityName] = Field(default_factory=list)
    skills: list[HeroSkillSource] = Field(default_factory=list)
    fighting_style: str | None = None
    attacks: list[HeroAttackSource] = Field(min_length=1)
    primary_attack_id: str
    visual: dict[str, str | None]
    source: str

    @model_validator(mode="after")
    def valid_primary_attack(self) -> "HeroBuildSource":
        if self.primary_attack_id not in {attack.id for attack in self.attacks}:
            raise ValueError("primary_attack_id must reference a declared hero attack.")
        return self
