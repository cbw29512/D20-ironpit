from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SorcererCombatLevel:
    level: int
    proficiency_bonus: int
    sorcery_points: int
    cantrips: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]


_ROWS = {
    1: (2, 0, 4, 2, _slots(2), ("sorcerer-spellcasting", "innate-sorcery")),
    2: (2, 2, 4, 4, _slots(3), ("font-of-magic", "metamagic")),
    3: (2, 3, 4, 6, _slots(4, 2), ("draconic-resilience",)),
    4: (2, 4, 5, 7, _slots(4, 3), ()),
    5: (3, 5, 5, 9, _slots(4, 3, 2), ("sorcerous-restoration",)),
    6: (3, 6, 5, 10, _slots(4, 3, 3), ("elemental-affinity-fire",)),
    7: (3, 7, 5, 11, _slots(4, 3, 3, 1), ("sorcery-incarnate",)),
    8: (3, 8, 5, 12, _slots(4, 3, 3, 2), ()),
    9: (4, 9, 5, 14, _slots(4, 3, 3, 3, 1), ()),
    10: (4, 10, 6, 15, _slots(4, 3, 3, 3, 2), ("metamagic-l10",)),
    11: (4, 11, 6, 16, _slots(4, 3, 3, 3, 2, 1), ()),
    12: (4, 12, 6, 16, _slots(4, 3, 3, 3, 2, 1), ()),
    13: (5, 13, 6, 17, _slots(4, 3, 3, 3, 2, 1, 1), ()),
    14: (5, 14, 6, 17, _slots(4, 3, 3, 3, 2, 1, 1), ("dragon-wings",)),
    15: (5, 15, 6, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), ()),
    16: (5, 16, 6, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), ()),
    17: (6, 17, 6, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), ("metamagic-l17",)),
    18: (6, 18, 6, 20, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), ("dragon-companion",)),
    19: (6, 19, 6, 21, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), ("sorcerer-epic-boon",)),
    20: (6, 20, 6, 22, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), ("arcane-apotheosis",)),
}

SORCERER_COMBAT_LEVELS = {
    level: SorcererCombatLevel(level, pb, points, cantrips, prepared, slots, add)
    for level, (pb, points, cantrips, prepared, slots, add) in _ROWS.items()
}
