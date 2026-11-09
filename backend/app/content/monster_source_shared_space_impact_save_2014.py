"""Source-proven shared-square impact save/Recharge components (2014).

Schema: source card owns target geometry, DC, damage, success scaling,
Prone rider and Recharge. Existing save/recharge/condition engines own
resolution. Thrown-body/object collisions remain UNSUPPORTED; do not
classify the complete source Action as battle-ready.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_shared_space_recharge_2014 import (
    source_shared_space_recharge_headers_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

# Entire printed outcome grammar, not an action-name or monster-ID switch.
# The collision riders are verified but intentionally NOT bound as damage.
_WHOLE = re.compile(
    r"On a failure, a target takes (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+) \+ (?P<bonus>\d+)\) "
    r"(?P<type>\w+) damage and is flung up (?P<fling>\d+) feet "
    r"away from the (?P<owner>[\w ]+) in a random direction and knocked prone\. "
    r"If a thrown target strikes an object, such as a wall or floor, "
    r"the target takes (?P<impact_average>\d+) "
    r"\((?P<impact_count>\d+)d(?P<impact_size>\d+)\) "
    r"(?P<impact_type>\w+) damage for every (?P<impact_step>\d+) feet it was thrown\. "
    r"If the target is thrown at another creature, that creature must succeed "
    r"on a DC (?P<collision_dc>\d+) Dexterity saving throw or take the same "
    r"damage and be knocked prone\. If the saving throw is successful, "
    r"the target takes half the (?P=type) damage and isn't flung away or knocked prone\.",
    re.IGNORECASE,
)


def source_proven_shared_space_impact_saves_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Extract only independently supported effects; leave collision blocked."""
    try:
        found: list[SaveCapabilityDefinition] = []
        for header in source_shared_space_recharge_headers_2014(monster):
            match = _WHOLE.fullmatch(
                " ".join(header.unbound_outcomes.replace("’", "'").split())
            )
            if match is None:
                continue
            n = {
                key: int(value) for key, value in match.groupdict().items()
                if key not in {"type", "impact_type", "owner"}
            }
            if (
                not 1 <= n["count"] <= 40 or not 2 <= n["size"] <= 100
                or not 1 <= n["impact_count"] <= 40
                or not 2 <= n["impact_size"] <= 100
                or n["average"] != (n["count"] * (n["size"] + 1)) // 2 + n["bonus"]
                or n["impact_average"] != (
                    n["impact_count"] * (n["impact_size"] + 1)
                ) // 2
                or n["collision_dc"] != header.save_dc
                or n["fling"] <= 0 or n["impact_step"] <= 0
            ):
                continue
            found.append(SaveCapabilityDefinition(
                id=header.action_id,
                name=header.source_name,
                save_ability=header.save_ability,
                dc=header.save_dc,
                range_ft=0,
                max_targets=20,
                target_scope="all-other-creatures",
                area=AreaTargeting(shape="shared-space", origin="self"),
                damage=DiceSpec(
                    count=n["count"], size=n["size"], bonus=n["bonus"],
                ),
                damage_type=match["type"].casefold(),
                success_damage="half",
                # Ordinary Prone until stood up, not a fabricated duration.
                failed_save_timed_effect=FailedSaveTimedEffect(
                    effect_id="prone", expiry_timing=None,
                ),
                # No push: coincident squares have no unique outward ray,
                # and locked Pit arena movement ignores fling/relocation.
                resource_id=header.action_id,
                resource_cost=1,
            ))
        return found
    except Exception:
        logger.exception(
            "Failed source-proven shared-space impact save binding: %s",
            monster.id,
        )
        raise
