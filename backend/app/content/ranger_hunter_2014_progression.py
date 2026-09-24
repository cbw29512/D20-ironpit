from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Ranger2014Level:
    level: int
    proficiency_bonus: int
    spells_known: int
    spell_slots: tuple[int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int]:
    return tuple((*values, *([0] * (5 - len(values)))))  # type: ignore[return-value]


_ROWS = {
    1: (2, 0, _slots(), ("favored-enemy", "natural-explorer")),
    2: (2, 2, _slots(2), ("fighting-style", "spellcasting")),
    3: (2, 3, _slots(3), ("primeval-awareness", "hunter-colossus-slayer")),
    4: (2, 3, _slots(3), ("ability-score-improvement",)),
    5: (3, 4, _slots(4, 2), ("extra-attack",)),
    6: (3, 4, _slots(4, 2), ("favored-enemy-improvement", "natural-explorer-improvement")),
    7: (3, 5, _slots(4, 3), ("hunter-multiattack-defense",)),
    8: (3, 5, _slots(4, 3), ("ability-score-improvement", "lands-stride")),
    9: (4, 6, _slots(4, 3, 2), ()),
    10: (4, 6, _slots(4, 3, 2), ("natural-explorer-improvement", "hide-in-plain-sight")),
    11: (4, 7, _slots(4, 3, 3), ("hunter-volley",)),
    12: (4, 7, _slots(4, 3, 3), ("ability-score-improvement",)),
    13: (5, 8, _slots(4, 3, 3, 1), ()),
    14: (5, 8, _slots(4, 3, 3, 1), ("favored-enemy-improvement", "vanish")),
    15: (5, 9, _slots(4, 3, 3, 2), ("hunter-evasion",)),
    16: (5, 9, _slots(4, 3, 3, 2), ("ability-score-improvement",)),
    17: (6, 10, _slots(4, 3, 3, 3, 1), ()),
    18: (6, 10, _slots(4, 3, 3, 3, 1), ("feral-senses",)),
    19: (6, 11, _slots(4, 3, 3, 3, 2), ("ability-score-improvement",)),
    20: (6, 11, _slots(4, 3, 3, 3, 2), ("foe-slayer",)),
}


RANGER_HUNTER_2014_LEVELS = {
    level: Ranger2014Level(level, pb, known, slots, features)
    for level, (pb, known, slots, features) in _ROWS.items()
}


def ranger_hunter_2014_level(level: int) -> Ranger2014Level:
    try:
        return RANGER_HUNTER_2014_LEVELS[level]
    except KeyError as exc:
        logger.exception("Invalid 2014 Hunter Ranger level %s.", level)
        raise ValueError("2014 Hunter Ranger level must be between 1 and 20.") from exc
