"""Source proofs for 2014 Actions that yield only out-of-arena information.

An information-only Action stays printed on the source card; it is not cast
in Iron Pit and never acquires a fabricated combat roll, resource, or buff.
These checks classify *source text*, not combat resolution by ability name.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Whole, inspected printed clauses. Extra combat-effective riders must fail
# closed instead of inheriting a permissive name-based exclusion.
_NONCOMBAT_ACTION_CLAUSES_2014 = {
    "Heart Sight": (
        "The sprite touches a creature and magically knows the creature's current "
        "emotional state. If the target fails a DC 10 Charisma saving throw, the "
        "sprite also knows the creature's alignment. Celestials, fiends, and "
        "undead automatically fail the saving throw."
    ),
}


def verified_nonactionable_action_2014(monster: SourceMonster2014, action_name: str) -> bool:
    """Allow a source Action only if its *entire* effect is proven informational."""
    try:
        if action_name not in monster.action_names:
            return False
        expected = _NONCOMBAT_ACTION_CLAUSES_2014.get(action_name)
        if expected is None:
            return False
        printed = source_sections_2014(monster.source_actions).get(action_name)
        if printed is None:
            return False
        normalize = lambda text: " ".join(text.casefold().replace("’", "'").split())
        return normalize(printed) == normalize(expected)
    except Exception:
        logger.exception(
            "2014 noncombat action proof failed for %s / %s",
            monster.id, action_name,
        )
        raise
