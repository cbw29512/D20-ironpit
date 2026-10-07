from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)
_ANTIMAGIC_SUSCEPTIBILITY = "Antimagic Susceptibility"


def terminal_effect_tags_2014(monster: SourceMonster2014) -> list[str]:
    """Map printed susceptibilities to reusable semantic effect tags."""
    try:
        return ["antimagic"] if _ANTIMAGIC_SUSCEPTIBILITY in monster.trait_names else []
    except Exception:
        logger.exception("Failed to bind 2014 terminal-effect tags for %s.", monster.name)
        raise


def bound_terminal_effect_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    return (
        frozenset({_ANTIMAGIC_SUSCEPTIBILITY})
        if terminal_effect_tags_2014(monster)
        else frozenset()
    )
