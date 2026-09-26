from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LandDruid2014Overlay:
    level: int
    features_added: tuple[str, ...]


LAND_DRUID_2014_OVERLAY: dict[int, LandDruid2014Overlay] = {
    2: LandDruid2014Overlay(2, ("bonus-cantrip", "natural-recovery")),
    3: LandDruid2014Overlay(3, ("circle-spells-2",)),
    5: LandDruid2014Overlay(5, ("circle-spells-3",)),
    6: LandDruid2014Overlay(6, ("lands-stride",)),
    7: LandDruid2014Overlay(7, ("circle-spells-4",)),
    9: LandDruid2014Overlay(9, ("circle-spells-5",)),
    10: LandDruid2014Overlay(10, ("natures-ward",)),
    14: LandDruid2014Overlay(14, ("natures-sanctuary",)),
}


def land_druid_2014_features(level: int) -> tuple[str, ...]:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Circle of the Land overlay covers levels 1 through 20.")
        features: list[str] = []
        for current in range(1, level + 1):
            row = LAND_DRUID_2014_OVERLAY.get(current)
            if row is None:
                continue
            features.extend(row.features_added)
        return tuple(features)
    except Exception:
        logger.exception("Failed to compile 2014 Circle of the Land features through level %s.", level)
        raise


def compiled_land_druid_2014_features(level: int) -> tuple[str, ...]:
    try:
        from app.content.druid_2014_progression import druid_2014_features

        return (*druid_2014_features(level), *land_druid_2014_features(level))
    except Exception:
        logger.exception("Failed to compose base Druid and Land overlay through level %s.", level)
        raise
