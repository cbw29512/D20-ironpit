"""2014 Divine Eminence -> shared bonus-action temporary on-hit radiant damage rider.

Source: Bonus Action, expend spell slot, melee weapon attacks deal extra 3d6 radiant ( +1d6 per slot level above 1st) until end of turn.

Reuses existing action-economy, limited-use spell-slot resource (from spellcasting binder), and typed on-hit damage rider primitives. No name dispatch. Mutation fails closed.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_DIVINE_EMINENCE = "Divine Eminence"
_PATTERN = re.compile(
    r"As a bonus action, the priest can expend a spell slot to cause its melee weapon attacks to magically deal an extra 10 \(3d6\) radiant damage to a target on a hit\. This benefit lasts until the end of the turn\. If the priest expends a spell slot of 2nd level or higher, the extra damage increases by 1d6 for each level above 1st\.",
    re.IGNORECASE | re.DOTALL,
)

def verified_divine_eminence_2014(monster: SourceMonster2014) -> bool:
    """Strict source match for the pinned 2014 Divine Eminence clause."""
    try:
        if _DIVINE_EMINENCE not in monster.trait_names:
            return False
        text = source_sections_2014(monster.source_traits).get(_DIVINE_EMINENCE, "")
        return bool(_PATTERN.search(text))
    except Exception:
        logger.exception("Failed to verify 2014 Divine Eminence for %s.", monster.name)
        return False
