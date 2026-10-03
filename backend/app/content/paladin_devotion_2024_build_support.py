from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.domain.character_builds import AbilityIncrease, AbilityScores

logger = logging.getLogger(__name__)


def build_paladin_2024_ability_progression(
    level: int,
) -> tuple[
    AbilityScores,
    list[str],
    list[AbilityIncrease],
    list[AbilityIncrease],
    AbilityScores,
]:
    """Build Aurelia's cumulative ability-score state through the requested level."""
    try:
        base = canonical_base_ability_scores("paladin")
        allowed = ["strength", "dexterity", "constitution"]
        background = canonical_background_increases("paladin", allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="strength", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="strength", amount=1),
                AbilityIncrease(ability="charisma", amount=1),
            ])
        if level >= 12:
            # Strength is capped; continue Aurelia's shared hybrid stat priority.
            advancement.append(AbilityIncrease(ability="charisma", amount=2))

        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return base, allowed, background, advancement, final
    except Exception:
        logger.exception(
            "Failed to build 2024 Paladin ability progression at level %s.",
            level,
        )
        raise
