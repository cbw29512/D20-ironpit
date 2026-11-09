"""Source-proven helper-rescue action; Whelm is data, not a resolver name."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_held_turn_damage_2014 import source_held_turn_damage_2014
from app.content.monster_shared_space_recharge_2014 import (
    source_shared_space_recharge_headers_2014,
)
from app.domain.grapple_rescue import GrappleRescueRule

logger = logging.getLogger(__name__)

_HELPER = re.compile(
    r"A creature within (?P<range>\d+) feet of the (?P<owner>[\w ]+) "
    r"can pull a creature or object out of it by taking an action to make a "
    r"DC (?P<dc>\d+) Strength and succeeding\.",
    re.IGNORECASE,
)


def source_grapple_rescue_rules_2014(
    monster: SourceMonster2014,
) -> list[GrappleRescueRule]:
    """Only complete, source-proven held-target actions grant helper checks."""
    try:
        # This full-source parser rejects extra riders, any second Grapple
        # action, unsupported source grammar, or altered printed averages.
        proved = {item.source_name for item in source_held_turn_damage_2014(monster)}
        rules = []
        for header in source_shared_space_recharge_headers_2014(monster):
            if header.source_name not in proved:
                continue
            matches = list(_HELPER.finditer(header.unbound_outcomes.replace("’", "'")))
            if len(matches) != 1:
                continue
            match = matches[0]
            distance, dc = int(match["range"]), int(match["dc"])
            if distance <= 0 or not 1 <= dc <= 40:
                continue
            rules.append(GrappleRescueRule(
                source_action_id=header.action_id,
                source_name=header.source_name,
                check_ability="strength",
                check_dc=dc,
                helper_range_ft=distance,
            ))
        return rules
    except Exception:
        logger.exception("Failed to bind source grapple helper rescue for %s", monster.id)
        raise
