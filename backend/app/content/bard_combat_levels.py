from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BardCombatLevel:
    level: int
    proficiency_bonus: int
    armor_class: int
    max_hp: int
    intelligence: int
    wisdom: int
    charisma: int
    bardic_die_size: int
    bardic_inspiration_uses: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()
    features_removed: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()
    source: str = ""


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]


def _r(level: int, pb: int, hp: int, intelligence: int, wisdom: int, charisma: int,
       bardic_die: int, prepared: int, slots: tuple[int, int, int, int, int, int, int, int, int], *,
       add: tuple[str, ...] = (), remove: tuple[str, ...] = (), ignored: tuple[str, ...] = (),
       source: str = "") -> BardCombatLevel:
    uses = (charisma - 10) // 2
    return BardCombatLevel(level, pb, 12, hp, intelligence, wisdom, charisma, bardic_die,
                           uses, prepared, slots, add, remove, ignored, source)


BARD_COMBAT_LEVELS: dict[int, BardCombatLevel] = {
    1: _r(1, 2, 8, 13, 15, 17, 6, 4, _slots(2), add=("bardic-inspiration", "bard-spellcasting", "magic-initiate-cleric"), source="D&D Beyond Basic Rules 2024: Bard 1; Acolyte background"),
    2: _r(2, 2, 13, 13, 15, 17, 6, 5, _slots(3), ignored=("expertise", "jack-of-all-trades"), source="D&D Beyond Basic Rules 2024: Bard 2"),
    3: _r(3, 2, 18, 13, 15, 17, 6, 6, _slots(4, 2), add=("bard-combat-spells-2",), source="D&D Beyond Basic Rules 2024: Bard 3"),
    4: _r(4, 2, 23, 13, 15, 19, 6, 7, _slots(4, 3), source="D&D Beyond Basic Rules 2024: Bard 4 Ability Score Improvement (+2 Charisma)"),
    5: _r(5, 3, 28, 13, 15, 19, 8, 9, _slots(4, 3, 2), add=("font-of-inspiration", "bard-combat-spells-3"), source="D&D Beyond Basic Rules 2024: Bard 5 Font of Inspiration"),
    6: _r(6, 3, 33, 13, 15, 19, 8, 10, _slots(4, 3, 3), source="D&D Beyond Basic Rules 2024: Bard 6"),
    7: _r(7, 3, 38, 13, 15, 19, 8, 11, _slots(4, 3, 3, 1), add=("countercharm", "bard-combat-spells-4"), source="D&D Beyond Basic Rules 2024: Bard 7 Countercharm"),
    8: _r(8, 3, 43, 13, 16, 20, 8, 12, _slots(4, 3, 3, 2), source="D&D Beyond Basic Rules 2024: Bard 8 Ability Score Improvement (+1 Charisma, +1 Wisdom)"),
    9: _r(9, 4, 48, 13, 16, 20, 8, 14, _slots(4, 3, 3, 3, 1), add=("bard-combat-spells-5",), ignored=("expertise-2",), source="D&D Beyond Basic Rules 2024: Bard 9"),
    10: _r(10, 4, 53, 13, 16, 20, 10, 15, _slots(4, 3, 3, 3, 2), add=("magical-secrets",), source="D&D Beyond Basic Rules 2024: Bard 10 Magical Secrets"),
    11: _r(11, 4, 58, 13, 16, 20, 10, 16, _slots(4, 3, 3, 3, 2, 1), add=("bard-combat-spells-6",), source="D&D Beyond Basic Rules 2024: Bard 11 level 6 spells"),
    12: _r(12, 4, 63, 13, 18, 20, 10, 16, _slots(4, 3, 3, 3, 2, 1), source="D&D Beyond Basic Rules 2024: Bard 12 Ability Score Improvement (+2 Wisdom)"),
    13: _r(13, 5, 68, 13, 18, 20, 10, 17, _slots(4, 3, 3, 3, 2, 1, 1), add=("bard-combat-spells-7",), source="D&D Beyond Basic Rules 2024: Bard 13 level 7 spells"),
    14: _r(14, 5, 73, 13, 18, 20, 10, 17, _slots(4, 3, 3, 3, 2, 1, 1), source="D&D Beyond Basic Rules 2024: Bard 14"),
    15: _r(15, 5, 78, 13, 18, 20, 12, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), add=("bard-combat-spells-8",), source="D&D Beyond Basic Rules 2024: Bard 15 level 8 spells"),
    16: _r(16, 5, 83, 13, 20, 20, 12, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), source="D&D Beyond Basic Rules 2024: Bard 16 Ability Score Improvement (+2 Wisdom)"),
    17: _r(17, 6, 88, 13, 20, 20, 12, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), add=("bard-combat-spells-9",), source="D&D Beyond Basic Rules 2024: Bard 17 level 9 spells"),
    18: _r(18, 6, 93, 13, 20, 20, 12, 20, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), add=("superior-inspiration",), source="D&D Beyond Basic Rules 2024: Bard 18 Superior Inspiration"),
    19: _r(19, 6, 98, 14, 20, 20, 12, 21, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), add=("boon-spell-recall",), source="D&D Beyond Basic Rules 2024: Bard 19 Boon of Spell Recall (+1 Intelligence)"),
    20: _r(20, 6, 103, 14, 20, 20, 12, 22, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), add=("words-of-creation",), source="D&D Beyond Basic Rules 2024: Bard 20 Words of Creation"),
}


def bard_combat_features(level: int) -> tuple[str, ...]:
    if level not in BARD_COMBAT_LEVELS:
        raise ValueError(f"Bard level {level} must be between 1 and 20.")
    active: list[str] = []
    for current in range(1, level + 1):
        row = BARD_COMBAT_LEVELS[current]
        active = [feature for feature in active if feature not in row.features_removed]
        active.extend(feature for feature in row.features_added if feature not in active)
    return tuple(active)


def bard_arena_ignored(level: int) -> tuple[str, ...]:
    ignored: list[str] = []
    for current in range(1, level + 1):
        ignored.extend(item for item in BARD_COMBAT_LEVELS[current].arena_ignored if item not in ignored)
    return tuple(ignored)
