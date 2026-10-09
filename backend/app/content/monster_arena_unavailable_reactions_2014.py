from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

# Arena rules forbid adding combatants. Identify exactly the printed reaction
# that creates two new creatures; the source retains its full original wording.
_SPLIT_OFFSPRING = re.compile(r"\bsplits? into two new\b", re.IGNORECASE)
_SPLIT_TRIGGER = re.compile(r"\blightning or slashing damage\b", re.IGNORECASE)


def arena_unavailable_reaction_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Source-verified reactions whose only outcome violates the no-spawn rule."""
    try:
        source = monster.source_reactions or ""
        if not (_SPLIT_OFFSPRING.search(source) and _SPLIT_TRIGGER.search(source)):
            return frozenset()
        return frozenset(
            name for name in monster.reaction_names
            if name == "Split" and "<strong>Split.</strong>" in source
        )
    except Exception:
        logger.exception("Failed arena reaction classification for %s.", monster.name)
        raise
