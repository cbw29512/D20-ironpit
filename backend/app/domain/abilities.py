from __future__ import annotations

from enum import StrEnum


class Ability(StrEnum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class Skill(StrEnum):
    ATHLETICS = "athletics"
    ACROBATICS = "acrobatics"


SKILL_ABILITY: dict[Skill, Ability] = {
    Skill.ATHLETICS: Ability.STRENGTH,
    Skill.ACROBATICS: Ability.DEXTERITY,
}
