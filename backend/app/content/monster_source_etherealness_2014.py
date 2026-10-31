"""Source-proof arena-unavailable Etherealness mobility for 2014 cards.

Plane-shift/alternate-plane movement is unavailable under locked Pit rules.
Printed actions stay in immutable card metadata; no effect is silently cast.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# The complete source text must be a plane transition, with only supported
# visibility/cross-plane or carried-heartstone restrictions. No source IDs.
_PLANE_TRANSITION = re.compile(
    r"^The [a-z][a-z -]* (?:magically )?enters the Ethereal Plane from the "
    r"Material Plane, or vice versa\."
    r"(?: It is visible on the Material Plane while it is in the Border Ethereal, "
    r"and vice versa, yet it can't affect or be affected by anything on the other plane\."
    r"| To do so, the hag must have a heartstone in her possession\.)?$",
    re.IGNORECASE,
)


def verified_unavailable_etherealness_2014(
    monster: SourceMonster2014, action_name: str,
) -> bool:
    """Recognize wholly prohibited planar movement without using monster identity."""
    try:
        if action_name not in monster.action_names or action_name != "Etherealness":
            return False
        source = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(action_name)
        if source is None:
            return False
        normalized = " ".join(source.replace("’", "'").split())
        return _PLANE_TRANSITION.fullmatch(normalized) is not None
    except Exception:
        logger.exception(
            "Failed to inspect printed plane-transition action on %s/%s",
            monster.id, action_name,
        )
        raise
