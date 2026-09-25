from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Bard2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spells_known: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    bardic_inspiration_die: int
    features_added: tuple[str, ...] = ()
    source: str = "D&D Basic Rules 2014: Bard"


def _slots(*values: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    try:
        if len(values) > 9:
            raise ValueError("Bard spell-slot progression cannot exceed 9 spell levels.")
        return tuple((*values, *([0] * (9 - len(values)))))  # type: ignore[return-value]
    except Exception:
        logger.exception("Failed to build 2014 Bard spell-slot row from %s.", values)
        raise


BARD_2014_LEVELS: dict[int, Bard2014Level] = {
    1: Bard2014Level(1, 2, 2, 4, _slots(2), 6, ("bardic-inspiration", "spellcasting")),
    2: Bard2014Level(2, 2, 2, 5, _slots(3), 6, ("jack-of-all-trades", "song-of-rest-d6")),
    3: Bard2014Level(3, 2, 2, 6, _slots(4, 2), 6, ("bard-college", "expertise")),
    4: Bard2014Level(4, 2, 3, 7, _slots(4, 3), 6, ("ability-score-improvement",)),
    5: Bard2014Level(5, 3, 3, 8, _slots(4, 3, 2), 8, ("font-of-inspiration",)),
    6: Bard2014Level(6, 3, 3, 9, _slots(4, 3, 3), 8, ("countercharm",)),
    7: Bard2014Level(7, 3, 3, 10, _slots(4, 3, 3, 1), 8),
    8: Bard2014Level(8, 3, 3, 11, _slots(4, 3, 3, 2), 8, ("ability-score-improvement",)),
    9: Bard2014Level(9, 4, 3, 12, _slots(4, 3, 3, 3, 1), 8, ("song-of-rest-d8",)),
    10: Bard2014Level(10, 4, 4, 14, _slots(4, 3, 3, 3, 2), 10, ("expertise-2", "magical-secrets")),
    11: Bard2014Level(11, 4, 4, 15, _slots(4, 3, 3, 3, 2, 1), 10),
    12: Bard2014Level(12, 4, 4, 15, _slots(4, 3, 3, 3, 2, 1), 10, ("ability-score-improvement",)),
    13: Bard2014Level(13, 5, 4, 16, _slots(4, 3, 3, 3, 2, 1, 1), 10, ("song-of-rest-d10",)),
    14: Bard2014Level(14, 5, 4, 18, _slots(4, 3, 3, 3, 2, 1, 1), 10, ("magical-secrets-2",)),
    15: Bard2014Level(15, 5, 4, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1), 12),
    16: Bard2014Level(16, 5, 4, 19, _slots(4, 3, 3, 3, 2, 1, 1, 1), 12, ("ability-score-improvement",)),
    17: Bard2014Level(17, 6, 4, 20, _slots(4, 3, 3, 3, 2, 1, 1, 1, 1), 12, ("song-of-rest-d12",)),
    18: Bard2014Level(18, 6, 4, 22, _slots(4, 3, 3, 3, 3, 1, 1, 1, 1), 12, ("magical-secrets-3",)),
    19: Bard2014Level(19, 6, 4, 22, _slots(4, 3, 3, 3, 3, 2, 1, 1, 1), 12, ("ability-score-improvement",)),
    20: Bard2014Level(20, 6, 4, 22, _slots(4, 3, 3, 3, 3, 2, 2, 1, 1), 12, ("superior-inspiration",)),
}


def bard_2014_level(level: int) -> Bard2014Level:
    try:
        row = BARD_2014_LEVELS.get(level)
        if row is None:
            raise ValueError("2014 Bard progression covers levels 1 through 20.")
        return row
    except Exception:
        logger.exception("Failed to resolve 2014 Bard progression level %s.", level)
        raise


def bard_2014_features(level: int) -> tuple[str, ...]:
    try:
        bard_2014_level(level)
        features: list[str] = []
        for current in range(1, level + 1):
            for feature in BARD_2014_LEVELS[current].features_added:
                if feature not in features:
                    features.append(feature)
        return tuple(features)
    except Exception:
        logger.exception("Failed to compile 2014 Bard features through level %s.", level)
        raise
