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
    if len(values) > 5:
        raise ValueError("2014 Ranger spell slots cannot exceed 5 spell levels.")
    return tuple((*values, *([0] * (5 - len(values)))))  # type: ignore[return-value]


RANGER_2014_LEVELS: dict[int, Ranger2014Level] = {
    1: Ranger2014Level(1, 2, 0, _slots(), ("favored-enemy", "natural-explorer")),
    2: Ranger2014Level(2, 2, 2, _slots(2), ("fighting-style", "spellcasting")),
    3: Ranger2014Level(3, 2, 3, _slots(3), ("ranger-archetype", "primeval-awareness")),
    4: Ranger2014Level(4, 2, 3, _slots(3), ("ability-score-improvement",)),
    5: Ranger2014Level(5, 3, 4, _slots(4, 2), ("extra-attack",)),
    6: Ranger2014Level(6, 3, 4, _slots(4, 2), ("favored-enemy-improvement", "natural-explorer-improvement")),
    7: Ranger2014Level(7, 3, 5, _slots(4, 3), ()),
    8: Ranger2014Level(8, 3, 5, _slots(4, 3), ("ability-score-improvement", "lands-stride")),
    9: Ranger2014Level(9, 4, 6, _slots(4, 3, 2)),
    10: Ranger2014Level(10, 4, 6, _slots(4, 3, 2), ("natural-explorer-improvement", "hide-in-plain-sight")),
    11: Ranger2014Level(11, 4, 7, _slots(4, 3, 3)),
    12: Ranger2014Level(12, 4, 7, _slots(4, 3, 3), ("ability-score-improvement",)),
    13: Ranger2014Level(13, 5, 8, _slots(4, 3, 3, 1)),
    14: Ranger2014Level(14, 5, 8, _slots(4, 3, 3, 1), ("favored-enemy-improvement", "vanish")),
    15: Ranger2014Level(15, 5, 9, _slots(4, 3, 3, 2)),
    16: Ranger2014Level(16, 5, 9, _slots(4, 3, 3, 2), ("ability-score-improvement",)),
    17: Ranger2014Level(17, 6, 10, _slots(4, 3, 3, 3, 1)),
    18: Ranger2014Level(18, 6, 10, _slots(4, 3, 3, 3, 1), ("feral-senses",)),
    19: Ranger2014Level(19, 6, 11, _slots(4, 3, 3, 3, 2), ("ability-score-improvement",)),
    20: Ranger2014Level(20, 6, 11, _slots(4, 3, 3, 3, 2), ("foe-slayer",)),
}


def ranger_2014_level(level: int) -> Ranger2014Level:
    try:
        row = RANGER_2014_LEVELS.get(level)
        if row is None:
            raise ValueError("2014 Ranger progression covers levels 1 through 20.")
        return row
    except Exception:
        logger.exception("Failed to resolve 2014 Ranger progression level %s.", level)
        raise
