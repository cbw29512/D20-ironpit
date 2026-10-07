from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)
_POOR_DEPTH_PERCEPTION = "Poor Depth Perception"
_POOR_DEPTH_DISTANCE = re.compile(
    r"Poor Depth Perception\\..*?more than\\s+(\\d+)\\s+feet away",
    re.IGNORECASE | re.DOTALL,
)


def supports_poor_depth_perception_2014(monster: SourceMonster2014) -> bool:
    """Return whether printed distance Disadvantage is already covered by legal attack ranges."""
    try:
        if _POOR_DEPTH_PERCEPTION not in monster.trait_names:
            return False
        match = _POOR_DEPTH_DISTANCE.search(monster.source_traits or "")
        if match is None:
            raise ValueError(
                f"{monster.name} has Poor Depth Perception without a parseable distance."
            )
        threshold_ft = int(match.group(1))
        for attack in monster.attacks:
            if attack.kind == "melee":
                if attack.reach_ft > threshold_ft:
                    return False
                continue
            if attack.normal_range_ft is None or attack.long_range_ft is None:
                return False
            if attack.normal_range_ft > threshold_ft:
                return False
        return True
    except Exception:
        logger.exception(
            "Failed to classify 2014 Poor Depth Perception for %s.", monster.name
        )
        raise
