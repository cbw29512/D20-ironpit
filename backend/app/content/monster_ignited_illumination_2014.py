"""Fail-closed 2014 source proofs for noncombat light-radius traits.

The standard Pit has no lighting-dependent combat context. This validates
only the full printed lighting clauses; the cards remain immutable.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Full source bodies, not loose token matches. A future combat rider must fail.
_LIGHT_ONLY_CLAUSES = {
    "Ignited Illumination": (
        "as a bonus action, the magmin can set itself ablaze or extinguish its flames. "
        "while ablaze, the magmin sheds bright light in a 10-foot radius and dim "
        "light for an additional 10 feet."
    ),
    "Variable Illumination": (
        "the will-o'-wisp sheds bright light in a 5- to 20-foot radius and dim "
        "light for an additional number of feet equal to the chosen radius. "
        "the will-o'-wisp can alter the radius as a bonus action."
    ),
}


def source_proves_light_only_2014(
    monster: SourceMonster2014, trait_name: str,
) -> bool:
    """Check the complete printed trait and any unheaded continuations."""
    try:
        approved = _LIGHT_ONLY_CLAUSES.get(trait_name)
        if approved is None or trait_name not in monster.trait_names:
            return False
        paragraph = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get(trait_name)
        if paragraph is None:
            return False
        normalized = " ".join(paragraph.casefold().replace("’", "'").split())
        return normalized == approved
    except Exception:
        logger.exception("2014 source light-only proof failed for %s.", trait_name)
        raise


def source_proves_ignited_illumination_2014(monster: SourceMonster2014) -> bool:
    """Compatibility name for the source-local Magmin regression."""
    return source_proves_light_only_2014(monster, "Ignited Illumination")
