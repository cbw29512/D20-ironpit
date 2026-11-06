"""Source proof for a purely equipment-restriction trait in the 2014 arena.

Printed inability to wear/carry items is nonactionable when the creature
already has no equippable inventory or loadout changes in the Pit. This
classifier never changes the immutable card or a combatant's equipment.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# This is source-proven data, not a combatability-name resolver.
_EQUIPMENT_ONLY_CLAUSES = {
    "Ephemeral": "the will-o'-wisp can't wear or carry anything.",
}


def source_proves_equipment_only_trait_2014(
    monster: SourceMonster2014, trait_name: str,
) -> bool:
    """Reject altered clauses, missing traits and hidden combat riders."""
    try:
        expected = _EQUIPMENT_ONLY_CLAUSES.get(trait_name)
        if expected is None or trait_name not in monster.trait_names:
            return False
        source = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get(trait_name)
        if not source:
            return False
        normalized = " ".join(source.casefold().replace("’", "'").split())
        return normalized == expected
    except Exception:
        logger.exception(
            "2014 equipment-only trait source verification failed for %s.",
            trait_name,
        )
        raise
