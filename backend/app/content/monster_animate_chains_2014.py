from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)


def supports_animate_chains_arena_unavailable_2014(monster: SourceMonster2014) -> bool:
    """Source-proof Animate Chains then classify arena-unavailable.

    The standard Pit has no unworn/uncarried chains and does not create
    subordinate combatant objects. Printed text stays on the immutable card.
    """
    try:
        names = {name.casefold() for name in monster.action_names}
        if not any(name.startswith("animate chains") for name in names):
            return False
        text = (monster.source_actions or "").casefold()
        required = (
            "animate chains",
            "chains aren't being worn or carried",
            "within 60 feet",
            "animated chain is an object",
            "reverts to its inanimate state",
        )
        return all(phrase in text for phrase in required)
    except Exception:
        logger.exception("Failed to verify Animate Chains for %s.", monster.id)
        raise
