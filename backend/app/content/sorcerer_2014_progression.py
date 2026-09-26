from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Sorcerer2014Level:
    level: int
    proficiency_bonus: int
    sorcery_points: int
    cantrips_known: int
    spells_known: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    try:
        if len(values) > 9:
            raise ValueError("2014 Sorcerer spell slots cannot exceed 9 spell levels.")
        return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]
    except Exception:
        logger.exception("Failed to compile 2014 Sorcerer spell-slot row: %s.", values)
        raise


SORCERER_2014_LEVELS: dict[int, Sorcerer2014Level] = {
    1: Sorcerer2014Level(1, 2, 0, 4, 2, _slots(2), ("spellcasting", "sorcerous-origin")),
    2: Sorcerer2014Level(2, 2, 2, 4, 3, _slots(3), ("font-of-magic",)),
    3: Sorcerer2014Level(3, 2, 3, 4, 4, _slots(4, 2), ("metamagic",)),
    4: Sorcerer2014Level(4, 2, 4, 5, 5, _slots(4, 3), ("ability-score-improvement",)),
    5: Sorcerer2014Level(5, 3, 5, 5, 6, _slots(4, 3, 2)),
    6: Sorcerer2014Level(6, 3, 6, 5, 7, _slots(4, 3, 3), ("elemental-affinity",)),
    7: Sorcerer2014Level(7, 3, 7, 5, 8, _slots(4, 3, 3, 1)),
    8: Sorcerer2014Level(8, 3, 8, 5, 9, _slots(4, 3, 3, 2), ("ability-score-improvement",)),
    9: Sorcerer2014Level(9, 4, 9, 5, 10, _slots(4, 3, 3, 3, 1)),
    10: Sorcerer2014Level(10, 4, 10, 6, 11, _slots(4, 3, 3, 3, 2), ("metamagic-2",)),
    11: Sorcerer2014Level(11, 4, 11, 6, 12, _slots(4, 3, 3, 3, 2, 1)),
    12: Sorcerer2014Level(12, 4, 12, 6, 12, _slots(4, 3, 3, 3, 2, 1), ("ability-score-improvement",)),
    13: Sorcerer2014Level(13, 5, 13, 6, 13, _slots(4, 3, 3, 3, 2, 1, 1)),
    14: Sorcerer2014Level(14, 5, 14, 6, 13, _slots(4, 3, 3, 3, 2, 1, 1), ("dragon-wings",)),
    15: Sorcerer2014Level(15, 5, 15, 6, 14, _slots(4, 3, 3, 3, 2, 1, 1, 1)),
    16: Sorcerer2014Level(16, 5, 16, 6, 14, _slots(4, 3, 3, 3, 2, 1, 1, 1), ("ability-score-improvement",)),
    17: Sorcerer2014Level(17, 6, 17, 6, 15, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), ("metamagic-3",)),
    18: Sorcerer2014Level(18, 6, 18, 6, 15, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), ("draconic-presence",)),
    19: Sorcerer2014Level(19, 6, 19, 6, 15, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), ("ability-score-improvement",)),
    20: Sorcerer2014Level(20, 6, 20, 6, 15, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), ("sorcerous-restoration",)),
}


def sorcerer_2014_level(level: int) -> Sorcerer2014Level:
    try:
        row = SORCERER_2014_LEVELS.get(level)
        if row is None:
            raise ValueError("2014 Sorcerer progression covers levels 1 through 20.")
        return row
    except Exception:
        logger.exception("Failed to resolve 2014 Sorcerer progression level %s.", level)
        raise
