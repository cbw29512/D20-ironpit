from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WizardCombatLevel:
    level: int
    proficiency_bonus: int
    cantrips: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]


_ROWS = {
    1: (2, 3, 4, _slots(2), ("wizard-spellcasting", "arcane-recovery"), ("ritual-adept",)),
    2: (2, 3, 5, _slots(3), (), ("scholar",)),
    3: (2, 3, 6, _slots(4, 2), ("potent-cantrip", "evocation-savant", "wizard-combat-spells-2"), ()),
    4: (2, 4, 7, _slots(4, 3), (), ()),
    5: (3, 4, 9, _slots(4, 3, 2), ("wizard-combat-spells-3",), ("memorize-spell",)),
    6: (3, 4, 10, _slots(4, 3, 3), ("sculpt-spells",), ()),
    7: (3, 4, 11, _slots(4, 3, 3, 1), ("wizard-combat-spells-4",), ()),
    8: (3, 4, 12, _slots(4, 3, 3, 2), (), ()),
    9: (4, 4, 14, _slots(4, 3, 3, 3, 1), ("wizard-combat-spells-5",), ()),
    10: (4, 5, 15, _slots(4, 3, 3, 3, 2), ("empowered-evocation",), ()),
    11: (4, 5, 16, _slots(4, 3, 3, 3, 2, 1), ("wizard-combat-spells-6",), ()),
    12: (4, 5, 16, _slots(4, 3, 3, 3, 2, 1), (), ()),
    13: (5, 5, 17, _slots(4, 3, 3, 3, 2, 1, 1), ("wizard-combat-spells-7",), ()),
    14: (5, 5, 18, _slots(4, 3, 3, 3, 2, 1, 1), ("overchannel",), ()),
    15: (5, 5, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1), ("wizard-combat-spells-8",), ()),
    16: (5, 5, 21, _slots(4, 3, 3, 3, 2, 1, 1, 1), (), ()),
    17: (6, 5, 22, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), ("wizard-combat-spells-9",), ()),
    18: (6, 5, 23, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), ("spell-mastery",), ()),
    19: (6, 5, 24, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), ("wizard-epic-boon",), ()),
    20: (6, 5, 25, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), ("signature-spells",), ()),
}

WIZARD_COMBAT_LEVELS = {
    level: WizardCombatLevel(level, pb, cantrips, prepared, slots, add, ignored)
    for level, (pb, cantrips, prepared, slots, add, ignored) in _ROWS.items()
}
