from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LandCircleSpellTier:
    character_level: int
    spell_ids: tuple[str, str]


LAND_TYPE_2014 = "forest"
FOREST_CIRCLE_SPELLS_2014: tuple[LandCircleSpellTier, ...] = (
    LandCircleSpellTier(3, ("barkskin", "spider-climb")),
    LandCircleSpellTier(5, ("call-lightning", "plant-growth")),
    LandCircleSpellTier(7, ("divination", "freedom-of-movement")),
    LandCircleSpellTier(9, ("commune-with-nature", "tree-stride")),
)


def forest_circle_spell_ids_2014(level: int) -> tuple[str, ...]:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Land Druid level must be between 1 and 20.")
        return tuple(
            spell_id
            for tier in FOREST_CIRCLE_SPELLS_2014
            if level >= tier.character_level
            for spell_id in tier.spell_ids
        )
    except Exception:
        logger.exception("Failed to compile Forest circle spells through level %s.", level)
        raise
