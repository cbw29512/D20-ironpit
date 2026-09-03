from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RangerCombatLevel:
    level: int
    proficiency_bonus: int
    favored_enemy_uses: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int]
    features_added: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int]:
    return tuple((*values, *([0] * (5 - len(values)))))  # type: ignore[return-value]


_ROWS = {
    1: (2, 2, 2, _slots(2), ("ranger-spellcasting", "hunters-mark", "weapon-mastery"), ()),
    2: (2, 2, 3, _slots(2), ("fighting-style",), ("deft-explorer",)),
    3: (2, 2, 4, _slots(3), (), ()),
    4: (2, 2, 5, _slots(3), (), ()),
    5: (3, 3, 6, _slots(4, 2), ("extra-attack", "ranger-combat-spells-2"), ()),
    6: (3, 3, 6, _slots(4, 2), ("roving",), ()),
    7: (3, 3, 7, _slots(4, 3), (), ()),
    8: (3, 3, 7, _slots(4, 3), (), ()),
    9: (4, 4, 9, _slots(4, 3, 2), ("ranger-combat-spells-3",), ("expertise",)),
    10: (4, 4, 9, _slots(4, 3, 2), ("tireless",), ()),
    11: (4, 4, 10, _slots(4, 3, 3), (), ()),
    12: (4, 4, 10, _slots(4, 3, 3), (), ()),
    13: (5, 5, 11, _slots(4, 3, 3, 1), ("relentless-hunter", "ranger-combat-spells-4"), ()),
    14: (5, 5, 11, _slots(4, 3, 3, 1), ("natures-veil",), ()),
    15: (5, 5, 12, _slots(4, 3, 3, 2), (), ()),
    16: (5, 5, 12, _slots(4, 3, 3, 2), (), ()),
    17: (6, 6, 14, _slots(4, 3, 3, 3, 1), ("precise-hunter", "ranger-combat-spells-5"), ()),
    18: (6, 6, 14, _slots(4, 3, 3, 3, 1), ("feral-senses",), ()),
    19: (6, 6, 15, _slots(4, 3, 3, 3, 2), ("ranger-epic-boon",), ()),
    20: (6, 6, 15, _slots(4, 3, 3, 3, 2), ("foe-slayer",), ()),
}

RANGER_COMBAT_LEVELS = {
    level: RangerCombatLevel(level, pb, favored, prepared, slots, add, ignored)
    for level, (pb, favored, prepared, slots, add, ignored) in _ROWS.items()
}
