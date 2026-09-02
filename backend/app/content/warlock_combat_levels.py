from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WarlockCombatLevel:
    level: int
    proficiency_bonus: int
    invocation_count: int
    cantrips: int
    prepared_spells: int
    pact_slots: int
    pact_slot_level: int
    features_added: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


_ROWS = {
    1: (2, 1, 2, 2, 1, 1, ("eldritch-invocations", "pact-magic"), ()),
    2: (2, 3, 2, 3, 2, 1, ("magical-cunning",), ()),
    3: (2, 3, 2, 4, 2, 2, ("dark-ones-blessing", "fiend-combat-spells-2"), ()),
    4: (2, 3, 3, 5, 2, 2, (), ()),
    5: (3, 5, 3, 6, 2, 3, ("fiend-combat-spells-3",), ()),
    6: (3, 5, 3, 7, 2, 3, ("dark-ones-own-luck",), ()),
    7: (3, 6, 3, 8, 2, 4, ("fiend-combat-spells-4",), ()),
    8: (3, 6, 3, 9, 2, 4, (), ()),
    9: (4, 7, 3, 10, 2, 5, ("fiend-combat-spells-5",), ("contact-patron",)),
    10: (4, 7, 4, 10, 2, 5, ("fiendish-resilience",), ()),
    11: (4, 7, 4, 11, 3, 5, ("mystic-arcanum-6",), ()),
    12: (4, 8, 4, 11, 3, 5, (), ()),
    13: (5, 8, 4, 12, 3, 5, ("mystic-arcanum-7",), ()),
    14: (5, 8, 4, 12, 3, 5, ("hurl-through-hell",), ()),
    15: (5, 9, 4, 13, 3, 5, ("mystic-arcanum-8",), ()),
    16: (5, 9, 4, 13, 3, 5, (), ()),
    17: (6, 9, 4, 14, 4, 5, ("mystic-arcanum-9",), ()),
    18: (6, 10, 4, 14, 4, 5, (), ()),
    19: (6, 10, 4, 15, 4, 5, ("warlock-epic-boon",), ()),
    20: (6, 10, 4, 15, 4, 5, ("eldritch-master",), ()),
}

WARLOCK_COMBAT_LEVELS = {
    level: WarlockCombatLevel(level, pb, invocations, cantrips, prepared, slots, slot_level, add, ignored)
    for level, (pb, invocations, cantrips, prepared, slots, slot_level, add, ignored) in _ROWS.items()
}
