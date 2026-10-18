"""Bind a printed 2014 reaction-budget trait to a reusable combat policy."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)
_EVERY_TURN_REACTION = re.compile(
    r"\bcan take one reaction on every turn in (?:a )?combat\b",
    re.IGNORECASE,
)


def supports_reaction_each_turn_2014(monster: SourceMonster2014) -> bool:
    """Only accept the exact source-described per-creature-turn reaction budget."""
    try:
        if "Reactive" not in monster.trait_names:
            return False
        source = source_sections_2014(monster.source_traits).get("Reactive", "")
        return bool(_EVERY_TURN_REACTION.search(source))
    except Exception:
        logger.exception("Failed to verify 2014 reaction budget for %s.", monster.id)
        raise
