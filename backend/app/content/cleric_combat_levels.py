from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClericCombatLevel:
    level: int
    proficiency_bonus: int
    armor_class: int
    max_hp: int
    wisdom: int
    charisma: int
    channel_divinity_uses: int
    divine_spark_dice: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()
    features_removed: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()
    source: str = ""


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]


def _r(level: int, pb: int, hp: int, wisdom: int, charisma: int, channel: int,
       spark: int, slots: tuple[int, int, int, int, int, int, int, int, int], *,
       add: tuple[str, ...] = (), remove: tuple[str, ...] = (), ignored: tuple[str, ...] = (),
       source: str = "") -> ClericCombatLevel:
    return ClericCombatLevel(level, pb, 15, hp, wisdom, charisma, channel, spark, slots,
                             add, remove, ignored, source)


CLERIC_COMBAT_LEVELS: dict[int, ClericCombatLevel] = {
    1: _r(1, 2, 8, 17, 14, 0, 1, _slots(2), add=("cleric-spellcasting", "divine-order-protector"), source="D&D Beyond Basic Rules 2024: Cleric 1, Orc, Sage, Protector, Equipment"),
    2: _r(2, 2, 13, 17, 14, 2, 1, _slots(3), add=("divine-spark", "turn-undead"), source="D&D Beyond Basic Rules 2024: Cleric 2 Channel Divinity"),
    3: _r(3, 2, 18, 17, 14, 2, 1, _slots(4, 2), source="D&D Beyond Basic Rules 2024: Cleric 3 Cleric Subclass"),
    4: _r(4, 2, 23, 19, 14, 2, 1, _slots(4, 3), ignored=("mending",), source="D&D Beyond Basic Rules 2024: Cleric 4 Ability Score Improvement (+2 Wisdom)"),
    5: _r(5, 3, 28, 19, 14, 2, 1, _slots(4, 3, 2), add=("sear-undead", "cleric-combat-spells-3"), source="D&D Beyond Basic Rules 2024: Cleric 5 Sear Undead and level 3 spells"),
    6: _r(6, 3, 33, 19, 14, 3, 1, _slots(4, 3, 3), source="D&D Beyond Basic Rules 2024: Cleric 6 subclass feature"),
    7: _r(7, 3, 38, 19, 14, 3, 2, _slots(4, 3, 3, 1), add=("blessed-strikes", "cleric-combat-spells-4"), source="D&D Beyond Basic Rules 2024: Cleric 7 Blessed Strikes and level 4 spells"),
    8: _r(8, 3, 43, 20, 15, 3, 2, _slots(4, 3, 3, 2), source="D&D Beyond Basic Rules 2024: Cleric 8 Ability Score Improvement (+1 Wisdom, +1 Charisma)"),
    9: _r(9, 4, 48, 20, 15, 3, 2, _slots(4, 3, 3, 3, 1), add=("cleric-combat-spells-5",), source="D&D Beyond Basic Rules 2024: Cleric 9 level 5 spells"),
    10: _r(10, 4, 53, 20, 15, 3, 2, _slots(4, 3, 3, 3, 2), add=("divine-intervention",), source="D&D Beyond Basic Rules 2024: Cleric 10 Divine Intervention"),
    11: _r(11, 4, 58, 20, 15, 3, 2, _slots(4, 3, 3, 3, 2, 1), add=("cleric-combat-spells-6",), source="D&D Beyond Basic Rules 2024: Cleric 11 level 6 spells"),
    12: _r(12, 4, 63, 20, 17, 3, 2, _slots(4, 3, 3, 3, 2, 1), source="D&D Beyond Basic Rules 2024: Cleric 12 Ability Score Improvement (+2 Charisma)"),
    13: _r(13, 5, 68, 20, 17, 3, 3, _slots(4, 3, 3, 3, 2, 1, 1), add=("cleric-combat-spells-7",), source="D&D Beyond Basic Rules 2024: Cleric 13 level 7 spells; Divine Spark 3d8"),
    14: _r(14, 5, 73, 20, 17, 3, 3, _slots(4, 3, 3, 3, 2, 1, 1), add=("improved-blessed-strikes",), source="D&D Beyond Basic Rules 2024: Cleric 14 Improved Blessed Strikes"),
    15: _r(15, 5, 78, 20, 17, 3, 3, _slots(4, 3, 3, 3, 2, 1, 1, 1), add=("cleric-combat-spells-8",), source="D&D Beyond Basic Rules 2024: Cleric 15 level 8 spells"),
    16: _r(16, 5, 83, 20, 19, 3, 3, _slots(4, 3, 3, 3, 2, 1, 1, 1), source="D&D Beyond Basic Rules 2024: Cleric 16 Ability Score Improvement (+2 Charisma)"),
    17: _r(17, 6, 88, 20, 19, 3, 3, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), add=("cleric-combat-spells-9",), source="D&D Beyond Basic Rules 2024: Cleric 17 subclass feature and level 9 spells"),
    18: _r(18, 6, 93, 20, 19, 4, 4, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), source="D&D Beyond Basic Rules 2024: Cleric 18 Channel Divinity 4; Divine Spark 4d8"),
    19: _r(19, 6, 98, 20, 20, 4, 4, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), add=("boon-of-fate",), source="D&D Beyond Basic Rules 2024: Cleric 19 Boon of Fate (+1 Charisma)"),
    20: _r(20, 6, 103, 20, 20, 4, 4, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), add=("greater-divine-intervention",), source="D&D Beyond Basic Rules 2024: Cleric 20 Greater Divine Intervention"),
}


def cleric_combat_features(level: int) -> tuple[str, ...]:
    if level not in CLERIC_COMBAT_LEVELS:
        raise ValueError(f"Cleric level {level} must be between 1 and 20.")
    active: list[str] = []
    for current in range(1, level + 1):
        row = CLERIC_COMBAT_LEVELS[current]
        active = [feature for feature in active if feature not in row.features_removed]
        active.extend(feature for feature in row.features_added if feature not in active)
    return tuple(active)


def cleric_arena_ignored(level: int) -> tuple[str, ...]:
    ignored: list[str] = []
    for current in range(1, level + 1):
        ignored.extend(item for item in CLERIC_COMBAT_LEVELS[current].arena_ignored if item not in ignored)
    return tuple(ignored)
