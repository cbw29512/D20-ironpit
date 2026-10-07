from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.effect_removal import EffectTagConditionGrant

logger = logging.getLogger(__name__)
_ANTIMAGIC_SUSCEPTIBILITY = "Antimagic Susceptibility"


def effect_tag_condition_grants_2014(monster: SourceMonster2014) -> list[EffectTagConditionGrant]:
    try:
        if _ANTIMAGIC_SUSCEPTIBILITY not in monster.trait_names:
            return []
        return [EffectTagConditionGrant(
            source_id="antimagic-susceptibility", source_name=_ANTIMAGIC_SUSCEPTIBILITY,
            effect_tag="spell_dispelling", condition_id="stunned", duration_rounds=10,
        )]
    except Exception:
        logger.exception("Failed to bind incoming-effect condition grants for %s.", monster.name)
        raise


def terminal_effect_tags_2014(monster: SourceMonster2014) -> list[str]:
    """Map printed susceptibilities to reusable semantic effect tags."""
    try:
        return ["antimagic"] if _ANTIMAGIC_SUSCEPTIBILITY in monster.trait_names else []
    except Exception:
        logger.exception("Failed to bind 2014 terminal-effect tags for %s.", monster.name)
        raise


def bound_terminal_effect_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    try:
        return (
            frozenset({_ANTIMAGIC_SUSCEPTIBILITY})
            if terminal_effect_tags_2014(monster)
            else frozenset()
        )
    except Exception:
        logger.exception("Failed to classify terminal-effect traits for %s.", monster.name)
        raise
