from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Druid2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    wild_shape_uses: int
    max_wild_shape_cr: str | None
    wild_shape_swim: bool
    wild_shape_fly: bool
    wild_shape_unlimited: bool
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
    1: Druid2014Level(1, 2, 2, _slots(2), 0, None, False, False, False, ("spellcasting", "druidic")),
    2: Druid2014Level(2, 2, 2, _slots(3), 2, "1/4", False, False, False, ("wild-shape", "druid-circle", "bonus-cantrip", "natural-recovery")),
    3: Druid2014Level(3, 2, 2, _slots(4, 2), 2, "1/4", False, False, False, ("circle-spells-2",)),
    4: Druid2014Level(4, 2, 3, _slots(4, 3), 2, "1/2", True, False, False, ("ability-score-improvement", "wild-shape-improvement")),
    5: Druid2014Level(5, 3, 3, _slots(4, 3, 2), 2, "1/2", True, False, False, ("circle-spells-3",)),
    6: Druid2014Level(6, 3, 3, _slots(4, 3, 3), 2, "1/2", True, False, False, ("lands-stride",)),
    7: Druid2014Level(7, 3, 3, _slots(4, 3, 3, 1), 2, "1/2", True, False, False, ("circle-spells-4",)),
    8: Druid2014Level(8, 3, 3, _slots(4, 3, 3, 2), 2, "1", True, True, False, ("ability-score-improvement", "wild-shape-improvement")),
    9: Druid2014Level(9, 4, 3, _slots(4, 3, 3, 3, 1), 2, "1", True, True, False, ("circle-spells-5",)),
    10: Druid2014Level(10, 4, 4, _slots(4, 3, 3, 3, 2), 2, "1", True, True, False, ("natures-ward",)),
    11: Druid2014Level(11, 4, 4, _slots(4, 3, 3, 3, 2, 1), 2, "1", True, True, False),
    12: Druid2014Level(12, 4, 4, _slots(4, 3, 3, 3, 2, 1), 2, "1", True, True, False, ("ability-score-improvement",)),
    13: Druid2014Level(13, 5, 4, _slots(4, 3, 3, 3, 2, 1, 1), 2, "1", True, True, False),
    14: Druid2014Level(14, 5, 4, _slots(4, 3, 3, 3, 2, 1, 1), 2, "1", True, True, False, ("natures-sanctuary",)),
    15: Druid2014Level(15, 5, 4, _slots(4, 3, 3, 3, 2, 1, 1, 1), 2, "1", True, True, False),
    16: Druid2014Level(16, 5, 4, _slots(4, 3, 3, 3, 2, 1, 1, 1), 2, "1", True, True, False, ("ability-score-improvement",)),
    17: Druid2014Level(17, 6, 4, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), 2, "1", True, True, False),
    18: Druid2014Level(18, 6, 4, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), 2, "1", True, True, False, ("timeless-body", "beast-spells")),
    19: Druid2014Level(19, 6, 4, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), 2, "1", True, True, False, ("ability-score-improvement",)),
    20: Druid2014Level(20, 6, 4, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), 2, "1", True, True, True, ("archdruid",)),
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
