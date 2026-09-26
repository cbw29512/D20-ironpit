from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Druid2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    prepared_spells: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    wild_shape_uses: int
    max_wild_shape_cr: str | None
    wild_shape_swim: bool
    wild_shape_fly: bool
    features_added: tuple[str, ...] = ()
    source: str = "D&D Basic Rules 2014: Druid"


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    try:
        if len(values) > 9:
            raise ValueError("Druid spell-slot progression cannot exceed 9 spell levels.")
        return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]
    except Exception:
        logger.exception("Failed to build 2014 Druid spell-slot row from %s.", values)
        raise


DRUID_2014_LEVELS: dict[int, Druid2014Level] = {
    1: Druid2014Level(1, 2, 2, 4, _slots(2), 0, None, False, False, ("spellcasting", "druidic")),
    2: Druid2014Level(2, 2, 2, 5, _slots(3), 2, "1/4", False, False, ("wild-shape", "druid-circle", "bonus-cantrip", "natural-recovery")),
    3: Druid2014Level(3, 2, 2, 6, _slots(4, 2), 2, "1/4", False, False, ("circle-spells-2",)),
    4: Druid2014Level(4, 2, 3, 7, _slots(4, 3), 2, "1/2", True, False, ("ability-score-improvement", "wild-shape-improvement")),
    5: Druid2014Level(5, 3, 3, 8, _slots(4, 3, 2), 2, "1/2", True, False, ("circle-spells-3",)),
    6: Druid2014Level(6, 3, 3, 9, _slots(4, 3, 3), 2, "1/2", True, False, ("lands-stride",)),
    7: Druid2014Level(7, 3, 3, 10, _slots(4, 3, 3, 1), 2, "1/2", True, False, ("circle-spells-4",)),
    8: Druid2014Level(8, 3, 3, 11, _slots(4, 3, 3, 2), 2, "1", True, True, ("ability-score-improvement", "wild-shape-improvement")),
    9: Druid2014Level(9, 4, 3, 12, _slots(4, 3, 3, 3, 1), 2, "1", True, True, ("circle-spells-5",)),
    10: Druid2014Level(10, 4, 4, 13, _slots(4, 3, 3, 3, 2), 2, "1", True, True, ("natures-ward",)),
    11: Druid2014Level(11, 4, 4, 14, _slots(4, 3, 3, 3, 2, 1), 2, "1", True, True),
    12: Druid2014Level(12, 4, 4, 15, _slots(4, 3, 3, 3, 2, 1), 2, "1", True, True, ("ability-score-improvement",)),
    13: Druid2014Level(13, 5, 4, 16, _slots(4, 3, 3, 3, 2, 1, 1), 2, "1", True, True),
    14: Druid2014Level(14, 5, 4, 17, _slots(4, 3, 3, 3, 2, 1, 1), 2, "1", True, True, ("natures-sanctuary",)),
    15: Druid2014Level(15, 5, 4, 18, _slots(4, 3, 3, 3, 2, 1, 1, 1), 2, "1", True, True),
    16: Druid2014Level(16, 5, 4, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1), 2, "1", True, True, ("ability-score-improvement",)),
    17: Druid2014Level(17, 6, 4, 20, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), 2, "1", True, True),
    18: Druid2014Level(18, 6, 4, 21, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), 2, "1", True, True, ("timeless-body", "beast-spells")),
    19: Druid2014Level(19, 6, 4, 22, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), 2, "1", True, True, ("ability-score-improvement",)),
    20: Druid2014Level(20, 6, 4, 23, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), 2, "1", True, True, ("archdruid",)),
}


def druid_2014_level(level: int) -> Druid2014Level:
    try:
        row = DRUID_2014_LEVELS.get(level)
        if row is None:
            raise ValueError("2014 Druid progression covers levels 1 through 20.")
        return row
    except Exception:
        logger.exception("Failed to resolve 2014 Druid progression level %s.", level)
        raise


def druid_2014_features(level: int) -> tuple[str, ...]:
    try:
        druid_2014_level(level)
        features: list[str] = []
        for current in range(1, level + 1):
            for feature in DRUID_2014_LEVELS[current].features_added:
                if feature not in features:
                    features.append(feature)
        return tuple(features)
    except Exception:
        logger.exception("Failed to compile 2014 Druid features through level %s.", level)
        raise
