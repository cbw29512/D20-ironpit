from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.targeting_overrides import TurnStartTargetingOverrideRule

logger = logging.getLogger(__name__)
_BERSERK_THRESHOLD = re.compile(
    r"Berserk.*?starts its turn with\s+(\d+)\s+hit points or fewer.*?"
    r"roll a d6\. On a 6,.*?goes berserk.*?"
    r"attacks the nearest creature it can see.*?"
    r"until it is destroyed or regains all its hit points",
    re.IGNORECASE | re.DOTALL,
)


def turn_start_targeting_overrides_2014(
    monster: SourceMonster2014,
) -> list[TurnStartTargetingOverrideRule]:
    """Extract the shared, source-complete Berserk targeting core without claiming side clauses."""
    try:
        if "Berserk" not in monster.trait_names:
            return []
        match = _BERSERK_THRESHOLD.search(monster.source_traits or "")
        if match is None:
            raise ValueError(f"{monster.name} Berserk source text does not match the supported core.")
        return [TurnStartTargetingOverrideRule(
            source_id=f"{monster.id}-berserk",
            source_name="Berserk",
            max_current_hp=int(match.group(1)),
            die_size=6,
            minimum_roll=6,
            target_mode="nearest_visible_creature",
            ends_on_full_hp=True,
        )]
    except Exception:
        logger.exception("Failed to bind 2014 targeting override for %s.", monster.name)
        raise
