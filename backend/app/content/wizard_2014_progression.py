from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Wizard2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    try:
        if len(values) > 9:
            raise ValueError("2014 Wizard spell slots cannot exceed 9 spell levels.")
        return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]
    except Exception:
        logger.exception("Failed to compile 2014 Wizard spell-slot row: %s.", values)
        raise


WIZARD_2014_LEVELS: dict[int, Wizard2014Level] = {
    1: Wizard2014Level(1, 2, 3, _slots(2), ("spellcasting", "arcane-recovery")),
    2: Wizard2014Level(2, 2, 3, _slots(3), ("evocation-savant", "sculpt-spells")),
    3: Wizard2014Level(3, 2, 3, _slots(4, 2)),
    4: Wizard2014Level(4, 2, 4, _slots(4, 3), ("ability-score-improvement",)),
    5: Wizard2014Level(5, 3, 4, _slots(4, 3, 2)),
    6: Wizard2014Level(6, 3, 4, _slots(4, 3, 3), ("potent-cantrip",)),
    7: Wizard2014Level(7, 3, 4, _slots(4, 3, 3, 1)),
    8: Wizard2014Level(8, 3, 4, _slots(4, 3, 3, 2), ("ability-score-improvement",)),
    9: Wizard2014Level(9, 4, 4, _slots(4, 3, 3, 3, 1)),
    10: Wizard2014Level(10, 4, 5, _slots(4, 3, 3, 3, 2), ("empowered-evocation",)),
    11: Wizard2014Level(11, 4, 5, _slots(4, 3, 3, 3, 2, 1)),
    12: Wizard2014Level(12, 4, 5, _slots(4, 3, 3, 3, 2, 1), ("ability-score-improvement",)),
    13: Wizard2014Level(13, 5, 5, _slots(4, 3, 3, 3, 2, 1, 1)),
    14: Wizard2014Level(14, 5, 5, _slots(4, 3, 3, 3, 2, 1, 1), ("overchannel",)),
    15: Wizard2014Level(15, 5, 5, _slots(4, 3, 3, 3, 2, 1, 1, 1)),
    16: Wizard2014Level(16, 5, 5, _slots(4, 3, 3, 3, 2, 1, 1, 1), ("ability-score-improvement",)),
    17: Wizard2014Level(17, 6, 5, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1)),
    18: Wizard2014Level(18, 6, 5, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), ("spell-mastery",)),
    19: Wizard2014Level(19, 6, 5, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), ("ability-score-improvement",)),
    20: Wizard2014Level(20, 6, 5, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), ("signature-spells",)),
}


def wizard_2014_level(level: int) -> Wizard2014Level:
    try:
        row = WIZARD_2014_LEVELS.get(level)
        if row is None:
            raise ValueError("2014 Wizard progression covers levels 1 through 20.")
        return row
    except Exception:
        logger.exception("Failed to resolve 2014 Wizard progression level %s.", level)
        raise
