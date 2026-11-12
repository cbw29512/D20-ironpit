"""2014 innate source-to-typed-zone binding, with no named runtime resolver.

Unrecognized source clauses never gain a free damaging spell. Generic
placed-zone, saves, terrain, resource usage and concentration run both editions.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_source_2014 import (
    innate_spell_save_dc_2014, innate_spells_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_angelic_innate_2014 import (
    source_proven_angelic_arena_exclusions_2014,
)
from app.content.shared_zone_spells_2014 import (
    insect_plague_2014, wall_of_fire_2014,
)
from app.domain.persistent_save_zones import PersistentSaveZoneAction

logger = logging.getLogger(__name__)


def source_supported_innate_zones_2014(
    monster: SourceMonster2014,
) -> list[PersistentSaveZoneAction]:
    """Compile exact source-proven spells into existing declarative zone data."""
    try:
        dc = innate_spell_save_dc_2014(monster)
        if dc is None:
            return []
        allowed_plague = bool(source_proven_angelic_arena_exclusions_2014(monster))
        zones: list[PersistentSaveZoneAction] = []
        for spell in innate_spells_2014(monster):
            spell_id = spell.get("id")
            if spell_id == "wall-of-fire":
                # The wall remains reference-only under global no-wall policy.
                zones.append(wall_of_fire_2014(dc).model_copy(
                    update={"resource_id": "wall-of-fire"},
                ))
            elif spell_id == "insect-plague" and allowed_plague:
                zones.append(insect_plague_2014(dc).model_copy(
                    update={"resource_id": "insect-plague"},
                ))
        return zones
    except Exception:
        logger.exception("2014 source-native zone binding failed for %s.", monster.id)
        raise
