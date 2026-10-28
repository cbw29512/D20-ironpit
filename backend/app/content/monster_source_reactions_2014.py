"""Source-verified 2014 reaction bindings for Shield and Spell Reflection.

Reuses existing reaction/AC and spell-redirect primitives. No name dispatch.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)


def supports_shield_reaction_2014(monster: SourceMonster2014) -> bool:
    """Shield: +2 AC to amulet wearer within 5 ft on attack against wearer."""
    try:
        text = (monster.source_reactions or "").lower()
        return (
            "shield" in (monster.reaction_names or [])
            and "+2" in text
            and "bonus to the wearer's ac" in text
            and "within 5 feet" in text
        )
    except Exception:
        logger.exception("Failed to verify Shield reaction for %s.", monster.id)
        raise


def supports_spell_reflection_reaction_2014(monster: SourceMonster2014) -> bool:
    """Spell Reflection: redirect on successful save or miss to visible creature within 30 ft."""
    try:
        text = (monster.source_reactions or "").lower()
        return (
            "spell reflection" in (monster.reaction_names or [])
            and "successful saving throw against a spell" in text
            and "spell attack misses" in text
            and "within 30 feet" in text
        )
    except Exception:
        logger.exception("Failed to verify Spell Reflection for %s.", monster.id)
        raise


def supports_source_reaction_2014(monster: SourceMonster2014) -> bool:
    return supports_shield_reaction_2014(monster) or supports_spell_reflection_reaction_2014(monster)
