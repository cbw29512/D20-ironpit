"""Source-verified 2014 darkvision that also sees through magical darkness."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_TRAIT = re.compile(
    r"Magical darkness doesn't impede the [a-z][a-z -]*'s darkvision\.",
    re.IGNORECASE,
)
_DARKVISION = re.compile(r"\bdarkvision\s+(\d+)\s*ft\.", re.IGNORECASE)


def source_proven_magical_darkness_sight_ft_2014(
    monster: SourceMonster2014,
) -> int:
    """Return a typed sight range, zero if the complete printed proof fails."""
    try:
        if "Devil's Sight" not in monster.trait_names:
            return 0
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Devil's Sight", "")
        if _TRAIT.fullmatch(printed) is None:
            return 0
        found = _DARKVISION.findall(monster.senses or "")
        mentions = re.findall(r"\bdarkvision\b", monster.senses or "", re.IGNORECASE)
        if len(found) != 1 or len(mentions) != 1:
            return 0
        distance_ft = int(found[0])
        return distance_ft if 1 <= distance_ft <= 1000 else 0
    except Exception:
        logger.exception("Failed 2014 magical-darkness sight source proof for %s.", monster.id)
        raise
