"""Strict 2014 source proof for a lighting-only voluntary bonus-action trait.

The standard Pit has no light/darkness-dependent combat geometry; changing
light emission does not affect a fight. Printed text remains immutable.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_PRINTED_LIGHT_ONLY_CLAUSE = (
    "as a bonus action, the magmin can set itself ablaze or extinguish its flames. "
    "while ablaze, the magmin sheds bright light in a 10-foot radius and dim "
    "light for an additional 10 feet."
)


def source_proves_ignited_illumination_2014(monster: SourceMonster2014) -> bool:
    """Fail closed on any altered action, radius, duration, or added rider."""
    try:
        if "Ignited Illumination" not in monster.trait_names:
            return False
        paragraph = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Ignited Illumination")
        if paragraph is None:
            return False
        normalized = " ".join(paragraph.casefold().replace("’", "'").split())
        return normalized == _PRINTED_LIGHT_ONLY_CLAUSE
    except Exception:
        logger.exception("2014 Ignited Illumination source proof failed.")
        raise
