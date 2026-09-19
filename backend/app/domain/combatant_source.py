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


class HeroLevelDelta(BaseModel):
    level: int = Field(ge=1, le=20)
    proficiency_bonus: int | None = Field(default=None, ge=2, le=6)
    max_hp: int | None = Field(default=None, ge=1)
    ability_scores: AbilityScoreDelta | None = None
    attack_count: int | None = Field(default=None, ge=1)
    weapon_masteries: list[str] | None = None
    resources: dict[str, int] = Field(default_factory=dict)
    capabilities_added: list[str] = Field(default_factory=list)
    capabilities_removed: list[str] = Field(default_factory=list)
    arena_ignored: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_level_one_foundation(self) -> "HeroLevelDelta":
        if self.level == 1:
            required = (self.proficiency_bonus, self.max_hp, self.ability_scores, self.attack_count)
            if any(value is None for value in required):
                raise ValueError("Level 1 must define proficiency, HP, ability scores, and attack count.")
        return self


class HeroProgressionSource(BaseModel):
    schema_version: int = 1
    edition: Literal["2014", "2024"]
    class_id: str
    source: str
    levels: list[HeroLevelDelta] = Field(min_length=1)

    @model_validator(mode="after")
    def contiguous_unique_levels(self) -> "HeroProgressionSource":
        actual = [row.level for row in self.levels]
        expected = list(range(1, max(actual) + 1))
        if actual != expected:
            raise ValueError(f"Progression levels must be ordered and contiguous: expected {expected}, got {actual}.")
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


class HeroIdentitySource(BaseModel):
    id: str
    name: str
    class_id: str
    subclass_id: str
    build_id: str
    species: str
    background: str
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
