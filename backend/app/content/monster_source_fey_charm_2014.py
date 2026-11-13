"""2014 Fey Charm: exact source -> shared save, Charmed and source ownership.

Data, not creature identity, owns DC, target types, limits, immunity, and expiry.
Unlike obedience-based fiend Charm, Fey Charm never changes team/controller.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)

_PRINTED = re.compile(
    r"The dryad targets one humanoid or beast that she can see within "
    r"(?P<range>\d+) feet of her\. If the target can see the dryad, it must "
    r"succeed on a DC (?P<dc>\d+) Wisdom saving throw or be magically charmed\. "
    r"The charmed creature regards the dryad as a trusted friend to be heeded "
    r"and protected\. Although the target isn't under the dryad's control, it "
    r"takes the dryad's requests or actions in the most favorable way it can\. "
    r"Each time the dryad or its allies do anything harmful to the target, it "
    r"can repeat the saving throw, ending the effect on itself on a success\. "
    r"Otherwise, the effect lasts (?P<hours>\d+) hours or until the dryad dies, "
    r"is on a different plane of existence from the target, or ends the effect "
    r"as a bonus action\. If a target's saving throw is successful, the target "
    r"is immune to the dryad's Fey Charm for the next (?P<immunity>\d+) hours\. "
    r"The dryad can have no more than one humanoid and up to three beasts "
    r"charmed at a time\.",
    re.IGNORECASE,
)


def source_proven_fey_charm_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Compile only the complete printed action, without identity dispatch."""
    try:
        if "Fey Charm" not in monster.action_names:
            return []
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        printed = sections.get("Fey Charm", "")
        match = _PRINTED.fullmatch(" ".join(
            printed.replace("’", "'").split()
        ))
        if match is None:
            return []
        radius, dc, hours, immunity = (
            int(match[key]) for key in ("range", "dc", "hours", "immunity")
        )
        # Parsed values must stay consistent with the supported source duration,
        # the shared combat range and the match-scoped 24-hour immunity marker.
        if radius != 30 or dc != 14 or hours != 24 or immunity != 24:
            return []
        return [SaveCapabilityDefinition(
            id="fey-charm", name="Fey Charm", action_cost="action",
            save_ability="wisdom", dc=dc, range_ft=radius,
            requires_target_sight=True, requires_target_to_see_source=True,
            required_target_creature_types=["humanoid", "beast"],
            magical_effect=True, effect_tags=["charmed"],
            source_effect_immunity_on_success=True,
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="charmed",
                duration_rounds=hours * 60 * 10,
                expiry_timing="target_turn_end",
                repeat_save_ability="wisdom", repeat_save_dc=dc,
                repeat_save_timing=None,
                damage_repeat_save_trigger="source_or_allies",
                source_target_limits_by_creature_type={"humanoid": 1, "beast": 3},
                ends_if_source_dead=True,
                # Only successful saves grant immunity; capacity replacement,
                # expiration and source death do NOT grant immunity.
                source_effect_immunity_on_repeat_save_success=True,
            ),
            animation="charm",
        )]
    except Exception:
        logger.exception("Failed 2014 Fey Charm source binding.")
        raise
