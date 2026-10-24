from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_nonactionable_reaction_proofs_2014 import (
    verified_nonactionable_reaction_names_2014,
)

logger = logging.getLogger(__name__)

# Arena rules forbid adding combatants. Identify exactly the printed reaction
# that creates two new creatures; the source retains its full original wording.
_SPLIT_OFFSPRING = re.compile(r"\bsplits? into two new\b", re.IGNORECASE)
_SPLIT_TRIGGER = re.compile(r"\blightning or slashing damage\b", re.IGNORECASE)


def arena_unavailable_reaction_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return reactions intentionally excluded from combat resolution by source proof."""
    try:
        source = monster.source_reactions or ""
        unavailable = set(verified_nonactionable_reaction_names_2014(monster))
        if _SPLIT_OFFSPRING.search(source) and _SPLIT_TRIGGER.search(source):
            unavailable.update(
                name for name in monster.reaction_names
                if name == "Split" and "<strong>Split.</strong>" in source
            )
        return frozenset(unavailable)
    except Exception:
        logger.exception("Failed arena reaction classification for %s.", monster.name)
        raise
