"""Source-proven, per-caster 2014 innate spell AI exclusions.

These spells remain on the immutable printed source card. The returned IDs
only prevent the standard Iron Pit AI from selecting them; they do not claim
that the spells lack tabletop combat effects or disable them for other casters.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_fog_cloud_2014 import source_proven_innate_fog_cloud_2014
from app.content.monster_innate_elemental_inert_2014 import (
    source_proven_elemental_inert_spells_2014,
)
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_innate_nature_spells_2014 import source_proven_goodberry_ai_exclusion_2014
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_CLOUD_GIANT_AI_EXCLUSIONS = {
    "fly": ("fly", "per_day", 3),
    "telekinesis": ("telekinesis", "per_day", 3),
    "gaseous-form": ("gaseous form", "per_day", 1),
}


def source_proven_arena_ai_excluded_innate_spells_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Return only source-proven, arena-excluded spell IDs without monster dispatch."""
    try:
        elemental_excluded = (source_proven_elemental_inert_spells_2014(monster)
                              | source_proven_goodberry_ai_exclusion_2014(monster))
        # This proof verifies the complete printed Cloud Giant innate paragraph
        # and every parsed spell/use row, not a monster ID or display name.
        if not source_proven_innate_fog_cloud_2014(monster):
            return elemental_excluded
        rows = {
            str(row.get("id") or ""): row
            for row in innate_spells_2014(monster)
        }
        for spell_id, (name, usage, uses) in _CLOUD_GIANT_AI_EXCLUSIONS.items():
            row = rows.get(spell_id)
            if (
                row is None
                or row.get("name") != name
                or row.get("usage") != usage
                or row.get("uses_per_day") != uses
                or row.get("shared_pool") is not False
                or row.get("qualifier") is not None
            ):
                return elemental_excluded
        return elemental_excluded | frozenset(_CLOUD_GIANT_AI_EXCLUSIONS)
    except Exception:
        logger.exception(
            "2014 innate arena-AI exclusion proof failed for %s.", monster.id,
        )
        raise
