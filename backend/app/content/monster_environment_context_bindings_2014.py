"""Immutable 2014 environment reactions built from source-verified card traits."""
from __future__ import annotations

import logging

from app.content.environment_context_reactions import (
    sunlight_sensitivity_2014, sunlight_weakness_2014,
    verified_sunlight_weakness_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.environment_contexts import EnvironmentContextReaction

logger = logging.getLogger(__name__)


def environment_context_reactions_2014(
    monster: SourceMonster2014,
) -> list[EnvironmentContextReaction]:
    """Bind only source-proven permanent environmental passives."""
    try:
        reactions = []
        if _SUNLIGHT_SENSITIVITY in monster.trait_names:
            reactions.append(sunlight_sensitivity_2014())
        if verified_sunlight_weakness_2014(monster):
            reactions.append(sunlight_weakness_2014())
        return reactions
    except Exception:
        logger.exception(
            "Failed to bind 2014 environment-context reactions for %s.",
            monster.name,
        )
        raise
