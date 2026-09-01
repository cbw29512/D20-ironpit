from __future__ import annotations

from app.domain.class_loadouts import CasterClassId

FULL_STANDARD = (4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16, 17, 17, 18, 18, 19, 20, 21, 22)
SORCERER = (2, 4, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16, 17, 17, 18, 18, 19, 20, 21, 22)
WIZARD = (4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 16, 17, 18, 19, 21, 22, 23, 24, 25)
WARLOCK = (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15)
HALF_CASTER = (2, 3, 4, 5, 6, 6, 7, 7, 9, 9, 10, 10, 11, 11, 12, 12, 14, 14, 15, 15)

PREPARED_COUNTS: dict[CasterClassId, tuple[int, ...]] = {
    "bard": FULL_STANDARD,
    "cleric": FULL_STANDARD,
    "druid": FULL_STANDARD,
    "paladin": HALF_CASTER,
    "ranger": HALF_CASTER,
    "sorcerer": SORCERER,
    "warlock": WARLOCK,
    "wizard": WIZARD,
}

CASTING_ABILITIES: dict[CasterClassId, str] = {
    "bard": "charisma",
    "cleric": "wisdom",
    "druid": "wisdom",
    "paladin": "charisma",
    "ranger": "wisdom",
    "sorcerer": "charisma",
    "warlock": "charisma",
    "wizard": "intelligence",
}


def _validate_level(level: int) -> None:
    if not 1 <= level <= 20:
        raise ValueError("Character level must be between 1 and 20.")


def prepared_spell_count(class_id: CasterClassId, level: int) -> int:
    _validate_level(level)
    return PREPARED_COUNTS[class_id][level - 1]


def max_spell_level(class_id: CasterClassId, level: int) -> int:
    _validate_level(level)
    if class_id in {"paladin", "ranger"}:
        return min(5, (level + 3) // 4)
    if class_id == "warlock":
        return min(5, (level + 1) // 2)
    return min(9, (level + 1) // 2)


def mystic_arcanum_levels(level: int) -> tuple[int, ...]:
    _validate_level(level)
    return tuple(spell_level for spell_level, unlock in ((6, 11), (7, 13), (8, 15), (9, 17)) if level >= unlock)
