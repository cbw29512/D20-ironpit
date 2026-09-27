from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Warlock2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spells_known: int
    pact_slots: int
    pact_slot_level: int
    invocations_known: int
    mystic_arcanum_levels: tuple[int, ...] = ()


_ROWS = {
    1: (2, 2, 2, 1, 1, 0),
    2: (2, 2, 3, 2, 1, 2),
    3: (2, 2, 4, 2, 2, 2),
    4: (2, 3, 5, 2, 2, 2),
    5: (3, 3, 6, 2, 3, 3),
    6: (3, 3, 7, 2, 3, 3),
    7: (3, 3, 8, 2, 4, 4),
    8: (3, 3, 9, 2, 4, 4),
    9: (4, 3, 10, 2, 5, 5),
    10: (4, 4, 10, 2, 5, 5),
    11: (4, 4, 11, 3, 5, 5),
    12: (4, 4, 11, 3, 5, 6),
    13: (5, 4, 12, 3, 5, 6),
    14: (5, 4, 12, 3, 5, 6),
    15: (5, 4, 13, 3, 5, 7),
    16: (5, 4, 13, 3, 5, 7),
    17: (6, 4, 14, 4, 5, 7),
    18: (6, 4, 14, 4, 5, 8),
    19: (6, 4, 15, 4, 5, 8),
    20: (6, 4, 15, 4, 5, 8),
}


def warlock_2014_level(level: int) -> Warlock2014Level:
    if level not in _ROWS:
        raise ValueError("2014 Warlock level must be between 1 and 20.")
    pb, cantrips, spells, slots, slot_level, invocations = _ROWS[level]
    arcanum = tuple(
        spell_level
        for spell_level, unlock in ((6, 11), (7, 13), (8, 15), (9, 17))
        if level >= unlock
    )
    return Warlock2014Level(
        level=level,
        proficiency_bonus=pb,
        cantrips_known=cantrips,
        spells_known=spells,
        pact_slots=slots,
        pact_slot_level=slot_level,
        invocations_known=invocations,
        mystic_arcanum_levels=arcanum,
    )
