"""Source-exact fallback for 2014 Healing Touch lost during catalog ingestion.

Only adapts immutable printed card data to an existing universal HealingAction.
Live healing, resource usage, and supported removals remain in the shared engine.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.healing_actions import HealingAction

logger = logging.getLogger(__name__)

_TOUCH = re.compile(
    r"\((?P<uses>\d+)/Day\)\. The [a-z][a-z -]* touches another creature\. "
    r"The target magically regains (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+) \+ (?P<bonus>\d+)\) hit points "
    r"and is freed from any curse, disease, poison, blindness, or deafness\.",
    re.IGNORECASE,
)


def source_proven_missing_healing_touch_2014(
    monster: SourceMonster2014,
) -> tuple[HealingAction, int] | None:
    """Require a whole source clause and no existing parsed healing action."""
    try:
        if "Healing Touch" not in monster.action_names or monster.healing_actions:
            return None
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get("Healing Touch", "")
        match = _TOUCH.fullmatch(" ".join(printed.replace("’", "'").split()))
        if match is None:
            return None
        dice, size, bonus, average, uses = (
            int(match[key]) for key in ("count", "size", "bonus", "average", "uses")
        )
        if not (1 <= dice <= 40 and 2 <= size <= 100 and 1 <= uses <= 10):
            return None
        if dice * (size + 1) // 2 + bonus != average:
            return None
        return (
            HealingAction(
                id="healing-touch", name="Healing Touch", action_cost="action",
                range_ft=5, target_mode="other", dice_count=dice, dice_size=size,
                healing_bonus=bonus, resource_id="healing-touch", resource_cost=1,
                removable_conditions=["poisoned", "blinded", "deafened"],
                removal_effect_tags=["disease"], removes_all_curses=True,
                animation="healing",
            ),
            uses,
        )
    except Exception:
        logger.exception("Source Healing Touch audit failed for %s.", monster.id)
        raise
