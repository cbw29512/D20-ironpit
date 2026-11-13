"""Source-proven external appendage break via the universal Grapple rescue rule."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_source_damage_free_grapple_2014 import (
    _TRAIT, source_proven_damage_free_grapple_attacks_2014,
)
from app.domain.grapple_rescue import GrappleRescueRule

logger = logging.getLogger(__name__)


def source_breakable_grapple_rescue_rules_2014(
    monster: SourceMonster2014,
) -> list[GrappleRescueRule]:
    """Require the entire printed trait and its real supported Tendril attack."""
    try:
        traits = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        match = _TRAIT.fullmatch(traits.get("Grasping Tendrils", ""))
        if match is None:
            return []
        check_dc = int(match["break_dc"])
        if not 1 <= check_dc <= 40:
            return []
        output = []
        for attack in source_proven_damage_free_grapple_attacks_2014(monster):
            # "A creature" permits the held target or a nearby ally. In the
            # one-square Pit, interacting with its own attached appendage is
            # adjacent to the victim, not the possibly distant grappler.
            output.append(GrappleRescueRule(
                source_action_id=attack.id,
                source_name=attack.name,
                check_ability="strength",
                check_dc=check_dc,
                helper_range_ft=5,
                helper_range_anchor="held_target",
                allow_held_target=True,
                requires_breakable_object=True,
                release_verb="break",
            ))
        return output
    except Exception:
        logger.exception("Source-bound 2014 external Grapple break Action failed.")
        raise
