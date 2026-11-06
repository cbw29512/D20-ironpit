"""Source-prove end-turn recurring weapon-hit effects across 2014 cards."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.recurring_damage import OnHitRecurringDamage

logger = logging.getLogger(__name__)

# This is source grammar, not a name/monster-specific combat resolver.
_IGNITION = re.compile(
    r"if the target is a creature(?: or a flammable object)?, it ignites\. "
    r"until a creature takes an action to douse the fire, the target takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) (?P<type>\w+) "
    r"damage at the end of each of its turns\.",
    flags=re.IGNORECASE,
)


def source_end_turn_recurring_damage_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> OnHitRecurringDamage | None:
    """Return only fully source-proven hit/tick dice; douse range stays blocked."""
    try:
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "").strip()
        match = _IGNITION.search(section)
        if match is None or match.end() != len(section):
            return None
        # The ordinary attack parser owns its hit/damage fields; the recurring
        # clause must actually be attached to the same printed hit paragraph.
        if "Hit:" not in section[:match.start()]:
            return None
        count, sides, average = (
            int(match["count"]), int(match["sides"]), int(match["average"])
        )
        if not (1 <= count <= 40 and 2 <= sides <= 100):
            return None
        if average != count * (sides + 1) // 2:
            return None
        return OnHitRecurringDamage(
            effect_id="burning", dice_count=count, dice_size=sides,
            damage_type=match["type"].lower(),
            removal_action_ids=["douse-fire"],
        )
    except Exception:
        logger.exception("2014 recurring hit-effect source proof failed for %s.", monster.id)
        raise
