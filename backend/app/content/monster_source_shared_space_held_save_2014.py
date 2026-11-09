"""Source-verified shared-square failed-save Grapple/Recharge binding (2014).

A complete source proof is required before exposing the already-supported
save, damage, Grapple-capacity and Recharge components. Admission requires all source Action riders, including the 2014 suffocation
lifecycle, to be bound and independently source-proven.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_shared_space_recharge_2014 import (
    source_shared_space_recharge_headers_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_held_turn_damage_2014 import (
    source_held_turn_damage_2014,
)
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec, GrappleEffectDefinition
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

# This is a parameter extractor, NOT the full-action proof. The held-turn
# source binder verifies every trailing Whelm clause before this can match.
_INITIAL = re.compile(
    r"^On a failure, a target takes (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+) \+ (?P<bonus>\d+)\) "
    r"(?P<damage_type>[A-Za-z]+) damage\. "
    r"If it is Large or smaller, it is also grappled "
    r"\(escape DC (?P<escape_dc>\d+)\)\.",
    re.IGNORECASE,
)


def source_proven_shared_space_held_saves_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Bind complete source-proven save parameters using shared mechanics."""
    try:
        verified_labels = {
            rule.source_name.casefold()
            for rule in source_held_turn_damage_2014(monster)
        }
        if not verified_labels:
            return []
        result: list[SaveCapabilityDefinition] = []
        for header in source_shared_space_recharge_headers_2014(monster):
            if header.source_name.casefold() not in verified_labels:
                continue
            match = _INITIAL.match(
                " ".join(header.unbound_outcomes.replace("’", "'").split())
            )
            if match is None:
                continue
            count = int(match["count"])
            sides = int(match["size"])
            bonus = int(match["bonus"])
            # The printed average is an independent source-integrity guard.
            if int(match["average"]) != count * (sides + 1) // 2 + bonus:
                continue
            result.append(SaveCapabilityDefinition(
                id=header.action_id,
                name=header.source_name,
                save_ability=header.save_ability,
                dc=header.save_dc,
                range_ft=0,
                max_targets=20,
                target_scope="all-other-creatures",
                area=AreaTargeting(shape="shared-space", origin="self"),
                damage=DiceSpec(count=count, size=sides, bonus=bonus),
                damage_type=match["damage_type"].casefold(),
                success_damage="none",
                # Full printed source proof includes the successful-save exit.
                # The generic event logger honors Pit's no-relocation policy.
                successful_save_exits_source_space=True,
                grapple=GrappleEffectDefinition(
                    escape_dc=int(match["escape_dc"]),
                    max_target_size=CreatureSize.LARGE,
                    size_only_applies_to_grapple=True,
                    restrains=True,
                    max_active_grapples=2,
                    large_target_slot_cost=2,
                    prevents_breathing=True,
                    breathing_exempt_medium="water",
                ),
                resource_id=header.action_id,
                resource_cost=1,
            ))
        return result
    except Exception:
        logger.exception(
            "Failed source-verified shared-space held-save binding for %s.",
            monster.id,
        )
        raise
