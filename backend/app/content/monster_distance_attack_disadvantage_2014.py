from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)
_POOR_DEPTH_PERCEPTION = "Poor Depth Perception"
_DISTANCE_PATTERN = re.compile(
    r"Poor Depth Perception.*?more than\\s+(\\d+)\\s+feet",
    re.IGNORECASE | re.DOTALL,
)


def attack_disadvantage_beyond_ft_2014(monster: SourceMonster2014) -> int:
    """Parse a source-owned distance threshold for all-attack Disadvantage."""
    try:
        if _POOR_DEPTH_PERCEPTION not in monster.trait_names:
            return 0
        match = _DISTANCE_PATTERN.search(monster.source_traits or "")
        if match is None:
            raise ValueError(
                f"{monster.name} has Poor Depth Perception without a parseable distance threshold."
            )
        distance_ft = int(match.group(1))
        if distance_ft <= 0:
            raise ValueError(
                f"{monster.name} has invalid Poor Depth Perception distance {distance_ft}."
            )
        return distance_ft
    except Exception:
        logger.exception(
            "Failed to parse distance-based attack Disadvantage for %s.", monster.name
        )
        raise


def bound_distance_attack_disadvantage_traits_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Return source trait names fully represented by the shared distance rule."""
    return (
        frozenset({_POOR_DEPTH_PERCEPTION})
        if attack_disadvantage_beyond_ft_2014(monster) > 0
        else frozenset()
    )
