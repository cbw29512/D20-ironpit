from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaladinCombatLevel:
    level: int
    proficiency_bonus: int
    channel_divinity_uses: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int]
    lay_on_hands_pool: int
    features_added: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int]:
    return tuple((*values, *([0] * (5 - len(values)))))  # type: ignore[return-value]


_ROWS = {
    1: (2, 0, 2, _slots(2), ("lay-on-hands", "paladin-spellcasting", "weapon-mastery"), ()),
    2: (2, 0, 3, _slots(2), ("fighting-style", "paladins-smite"), ()),
    3: (2, 2, 4, _slots(3), ("channel-divinity", "sacred-weapon", "devotion-combat-spells-1"), ()),
    4: (2, 2, 5, _slots(3), (), ()),
    5: (3, 2, 6, _slots(4, 2), ("extra-attack", "devotion-combat-spells-2"), ("faithful-steed",)),
    6: (3, 2, 6, _slots(4, 2), ("aura-of-protection",), ()),
    7: (3, 2, 7, _slots(4, 3), ("aura-of-devotion",), ()),
    8: (3, 2, 7, _slots(4, 3), (), ()),
    9: (4, 2, 9, _slots(4, 3, 2), ("abjure-foes", "devotion-combat-spells-3"), ()),
    10: (4, 2, 9, _slots(4, 3, 2), ("aura-of-courage",), ()),
    11: (4, 3, 10, _slots(4, 3, 3), ("radiant-strikes",), ()),
    12: (4, 3, 10, _slots(4, 3, 3), (), ()),
    13: (5, 3, 11, _slots(4, 3, 3, 1), ("devotion-combat-spells-4",), ()),
    14: (5, 3, 11, _slots(4, 3, 3, 1), ("restoring-touch",), ()),
    15: (5, 3, 12, _slots(4, 3, 3, 2), ("smite-of-protection",), ()),
    16: (5, 3, 12, _slots(4, 3, 3, 2), (), ()),
    17: (6, 3, 14, _slots(4, 3, 3, 3, 1), ("devotion-combat-spells-5",), ()),
    18: (6, 3, 14, _slots(4, 3, 3, 3, 1), ("aura-expansion",), ()),
    19: (6, 3, 15, _slots(4, 3, 3, 3, 2), ("paladin-epic-boon",), ()),
    20: (6, 3, 15, _slots(4, 3, 3, 3, 2), ("holy-nimbus",), ()),
}

PALADIN_COMBAT_LEVELS = {
    level: PaladinCombatLevel(level, pb, channel, prepared, slots, 5 * level, add, ignored)
    for level, (pb, channel, prepared, slots, add, ignored) in _ROWS.items()
}
