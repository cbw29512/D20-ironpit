from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DruidCombatLevel:
    level: int
    proficiency_bonus: int
    armor_class: int
    max_hp: int
    intelligence: int
    wisdom: int
    charisma: int
    wild_shape_uses: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()
    features_removed: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()
    source: str = ""


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]


def _r(level: int, pb: int, hp: int, intelligence: int, wisdom: int, charisma: int,
       wild_shape: int, prepared: int, slots: tuple[int, int, int, int, int, int, int, int, int], *,
       add: tuple[str, ...] = (), remove: tuple[str, ...] = (), ignored: tuple[str, ...] = (),
       source: str = "") -> DruidCombatLevel:
    return DruidCombatLevel(level, pb, 16, hp, intelligence, wisdom, charisma, wild_shape,
                            prepared, slots, add, remove, ignored, source)


DRUID_COMBAT_LEVELS: dict[int, DruidCombatLevel] = {
    1: _r(1, 2, 8, 13, 17, 15, 0, 4, _slots(2), add=("druid-spellcasting", "primal-order-warden", "magic-initiate-cleric"), ignored=("druidic", "speak-with-animals"), source="D&D Beyond Basic Rules 2024: Druid 1; Warden Primal Order; Acolyte background"),
    2: _r(2, 2, 13, 13, 17, 15, 2, 5, _slots(3), add=("wild-shape",), ignored=("wild-companion",), source="D&D Beyond Basic Rules 2024: Druid 2 Wild Shape"),
    3: _r(3, 2, 18, 13, 17, 15, 2, 6, _slots(4, 2), add=("lands-aid", "land-arid-spells", "druid-combat-spells-2"), source="D&D Beyond Basic Rules 2024: Druid 3 Circle of the Land"),
    4: _r(4, 2, 23, 13, 19, 15, 2, 7, _slots(4, 3), source="D&D Beyond Basic Rules 2024: Druid 4 Ability Score Improvement (+2 Wisdom)"),
    5: _r(5, 3, 28, 13, 19, 15, 2, 9, _slots(4, 3, 2), add=("wild-resurgence", "druid-combat-spells-3"), source="D&D Beyond Basic Rules 2024: Druid 5 Wild Resurgence"),
    6: _r(6, 3, 33, 13, 19, 15, 3, 10, _slots(4, 3, 3), add=("natural-recovery",), source="D&D Beyond Basic Rules 2024: Druid 6 Circle of the Land Natural Recovery"),
    7: _r(7, 3, 38, 13, 19, 15, 3, 11, _slots(4, 3, 3, 1), add=("potent-spellcasting", "druid-combat-spells-4"), source="D&D Beyond Basic Rules 2024: Druid 7 Elemental Fury — Potent Spellcasting"),
    8: _r(8, 3, 43, 13, 20, 16, 3, 12, _slots(4, 3, 3, 2), source="D&D Beyond Basic Rules 2024: Druid 8 Ability Score Improvement (+1 Wisdom, +1 Charisma)"),
    9: _r(9, 4, 48, 13, 20, 16, 3, 14, _slots(4, 3, 3, 3, 1), add=("druid-combat-spells-5",), source="D&D Beyond Basic Rules 2024: Druid 9"),
    10: _r(10, 4, 53, 13, 20, 16, 3, 15, _slots(4, 3, 3, 3, 2), add=("natures-ward-fire",), source="D&D Beyond Basic Rules 2024: Druid 10 Circle of the Land Nature's Ward"),
    11: _r(11, 4, 58, 13, 20, 16, 3, 16, _slots(4, 3, 3, 3, 2, 1), add=("druid-combat-spells-6",), source="D&D Beyond Basic Rules 2024: Druid 11"),
    12: _r(12, 4, 63, 13, 20, 18, 3, 16, _slots(4, 3, 3, 3, 2, 1), source="D&D Beyond Basic Rules 2024: Druid 12 Ability Score Improvement (+2 Charisma)"),
    13: _r(13, 5, 68, 13, 20, 18, 3, 17, _slots(4, 3, 3, 3, 2, 1, 1), add=("druid-combat-spells-7",), source="D&D Beyond Basic Rules 2024: Druid 13"),
    14: _r(14, 5, 73, 13, 20, 18, 3, 17, _slots(4, 3, 3, 3, 2, 1, 1), add=("natures-sanctuary",), source="D&D Beyond Basic Rules 2024: Druid 14 Circle of the Land Nature's Sanctuary"),
    15: _r(15, 5, 78, 13, 20, 18, 3, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), add=("improved-potent-spellcasting", "druid-combat-spells-8"), remove=("potent-spellcasting",), source="D&D Beyond Basic Rules 2024: Druid 15 Improved Elemental Fury"),
    16: _r(16, 5, 83, 13, 20, 20, 3, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), source="D&D Beyond Basic Rules 2024: Druid 16 Ability Score Improvement (+2 Charisma)"),
    17: _r(17, 6, 88, 13, 20, 20, 4, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), add=("druid-combat-spells-9",), source="D&D Beyond Basic Rules 2024: Druid 17"),
    18: _r(18, 6, 93, 13, 20, 20, 4, 20, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), add=("beast-spells",), source="D&D Beyond Basic Rules 2024: Druid 18 Beast Spells"),
    19: _r(19, 6, 98, 14, 20, 20, 4, 21, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), add=("boon-dimensional-travel",), source="D&D Beyond Basic Rules 2024: Druid 19 Boon of Dimensional Travel (+1 Intelligence)"),
    20: _r(20, 6, 103, 14, 20, 20, 4, 22, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), add=("archdruid",), source="D&D Beyond Basic Rules 2024: Druid 20 Archdruid"),
}


def druid_combat_features(level: int) -> tuple[str, ...]:
    if level not in DRUID_COMBAT_LEVELS:
        raise ValueError(f"Druid level {level} must be between 1 and 20.")
    active: list[str] = []
    for current in range(1, level + 1):
        row = DRUID_COMBAT_LEVELS[current]
        active = [feature for feature in active if feature not in row.features_removed]
        active.extend(feature for feature in row.features_added if feature not in active)
    return tuple(active)


def druid_arena_ignored(level: int) -> tuple[str, ...]:
    ignored: list[str] = []
    for current in range(1, level + 1):
        ignored.extend(item for item in DRUID_COMBAT_LEVELS[current].arena_ignored if item not in ignored)
    return tuple(ignored)
