from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_PATTERN = re.compile(
    r"^Each creature within (?P<radius>\d+) feet of the .+? that can hear "
    r"(?:its|the .+?'s) .+? and that isn't an? (?P<excluded>[\w -]+) must "
    r"succeed on a DC (?P<dc>\d+) (?P<ability>\w+) saving throw or become "
    r"(?P<condition>\w+) until the end of the .+?'s next turn\. If a creature's "
    r"saving throw is successful, the creature is immune to the .+?'s .+? for "
    r"the next 24 hours\.$",
    re.IGNORECASE,
)


def source_proven_audible_turn_conditions_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Compile audible one-turn conditions with source-scoped success immunity."""
    try:
        result: list[SaveCapabilityDefinition] = []
        for name, body in source_sections_2014(monster.source_actions).items():
            match = _PATTERN.fullmatch(" ".join(body.split()))
            if match is None:
                continue
            action_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
            radius = int(match["radius"])
            condition = match["condition"].casefold()
            result.append(SaveCapabilityDefinition(
                id=action_id,
                name=name,
                save_ability=match["ability"].casefold(),
                dc=int(match["dc"]),
                range_ft=radius,
                max_targets=20,
                target_scope="all-other-creatures",
                area=AreaTargeting(shape="emanation", origin="self", radius_ft=radius),
                requires_target_hearing=True,
                excluded_target_creature_types=[match["excluded"].casefold()],
                effect_tags=[condition],
                failed_save_timed_effect=FailedSaveTimedEffect(
                    effect_id=condition,
                    duration_rounds=1,
                    expiry_timing="source_turn_end",
                ),
                source_effect_immunity_on_success=True,
                animation="sound-wave",
            ))
        return result
    except Exception:
        logger.exception("Failed to bind audible turn conditions for %s.", monster.id)
        raise
