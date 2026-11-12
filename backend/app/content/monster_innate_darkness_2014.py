"""Source-exact innate Darkness attached to the universal zone capability.

The spell's magical visual obscuration is the source of the fight-local debuff,
not the ordinary Blinded condition. Every value is source/card parameters.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_faerie_fire_2014 import (
    source_proven_innate_trio_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.suppression_zones import PersistentSuppressionZoneAction

logger = logging.getLogger(__name__)


def source_proven_innate_darkness_2014(
    monster: SourceMonster2014,
) -> list[PersistentSuppressionZoneAction]:
    """A fully validated innate 2014 spell, independent of creature name."""
    try:
        if source_proven_innate_trio_2014(monster) is None:
            return []
        return [PersistentSuppressionZoneAction(
            id="darkness", name="Darkness", level=2,
            action_cost="action", cast_range_ft=60, radius_ft=15,
            duration_rounds=100, concentration=True,
            deafens=False, blocks_verbal_spells=False,
            thunder_immunity=False, obscuration_kind="magical-darkness",
            resource_id="darkness", resource_cost=1, expends_spell_slot=False,
            animation="darkness", source="D&D Basic Rules 2014: Darkness",
        )]
    except Exception:
        logger.exception("2014 innate Darkness source audit failed for %s.", monster.id)
        raise
