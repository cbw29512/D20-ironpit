from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

CasterClassId = Literal[
    "bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard",
]
SpellRole = Literal["damage", "healing", "buff", "debuff", "control", "utility", "mixed"]
MeleeLoadoutKind = Literal["one-hander-shield", "two-handed", "dual-wield"]


class CanonicalSpellChoice(BaseModel):
    id: str
    name: str
    spell_level: int = Field(ge=0, le=9)
    min_character_level: int = Field(ge=1, le=20)
    role: SpellRole
    required_capabilities: list[str] = Field(default_factory=list)


class ClassSpellPackage(BaseModel):
    class_id: CasterClassId
    casting_ability: Literal["intelligence", "wisdom", "charisma"]
    spells: list[CanonicalSpellChoice] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_spells(self) -> "ClassSpellPackage":
        ids = [spell.id for spell in self.spells]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.class_id} canonical spell IDs must be unique.")
        return self

    def unlocked(self, character_level: int) -> list[CanonicalSpellChoice]:
        if not 1 <= character_level <= 20:
            raise ValueError("Character level must be between 1 and 20.")
        return [spell for spell in self.spells if spell.min_character_level <= character_level]


class MeleeLoadoutSelection(BaseModel):
    kind: MeleeLoadoutKind
    primary_ability: Literal["strength", "dexterity"]
