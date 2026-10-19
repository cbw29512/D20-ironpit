"""Source-verified 2014 visual fear Actions; no creature-name runtime dispatch."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

# Entire printed effect must match: do not silently omit a new source clause.
_VISUAL_FEAR_SOURCE = re.compile(
    r"Each non-undead creature within (?P<radius>\d+) feet of the banshee "
    r"that can see her must succeed on a DC (?P<dc>\d+) Wisdom saving throw "
    r"or be frightened for (?P<duration>\d+) minute\. "
    r"A frightened target can repeat the saving throw at the end of each "
    r"of its turns, with disadvantage if the banshee is within line of sight, "
    r"ending the effect on itself on a success\. "
    r"If a target's saving throw is successful or the effect ends for it, "
    r"the target is immune to the banshee's Horrifying Visage for the next "
    r"(?P<immunity>\d+) hours\.",
    flags=re.IGNORECASE,
)


def source_proven_visual_saves_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    """Only adapt the full pinned Action when its printed clauses all match."""
    try:
        name = "Horrifying Visage"
        if name not in monster.action_names:
            return []
        printed = source_sections_2014(monster.source_actions).get(name)
        if printed is None:
            return []
        normalized = " ".join(printed.replace("’", "'").split())
        match = _VISUAL_FEAR_SOURCE.fullmatch(normalized)
        if match is None or int(match["duration"]) != 1 or int(match["immunity"]) != 24:
            return []
        radius, dc = int(match["radius"]), int(match["dc"])
        if radius <= 0 or radius % 5:
            return []
        return [SaveCapabilityDefinition(
            id="horrifying-visage", name=name,
            save_ability="wisdom", dc=dc, range_ft=radius,
            area=AreaTargeting(shape="emanation", origin="self", radius_ft=radius),
            target_scope="all-other-creatures",
            requires_target_to_see_source=True,
            excluded_target_creature_types=["undead"],
            source_effect_immunity_on_success=True,
            effect_tags=["frightened"],
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="frightened", duration_rounds=10,
                expiry_timing="target_turn_end",
                repeat_save_ability="wisdom", repeat_save_dc=dc,
                repeat_save_timing="target_turn_end",
                repeat_save_disadvantage_while_source_visible=True,
                source_effect_immunity_on_end=True,
            ),
            animation="fear",
        )]
    except Exception:
        logger.exception("2014 source visual save proof failed for %s.", monster.id)
        raise
