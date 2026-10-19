"""Compile verified 2014 printed save-result Actions into universal save grammar.

This is *source adaptation*, never name-dispatched combat runtime behavior.
An unrecognized or changed printed rider must remain blocked by admission.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.combatants import DamageType
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

# Exact effect grammar, with source-derived numbers (not literals in resolvers).
_WAIL_SOURCE = re.compile(
    r"The banshee releases a mournful wail, provided that she isn't in sunlight\. "
    r"This wail has no effect on constructs and undead\. "
    r"All other creatures within (?P<radius>\d+) feet of her that can hear her "
    r"must make a DC (?P<dc>\d+) Constitution saving throw\. "
    r"On a failure, a creature drops to 0 hit points\. "
    r"On a success, a creature takes (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+)\) psychic damage\.",
    flags=re.IGNORECASE,
)


def source_proven_asymmetric_saves_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Bind only full printed asymmetric-save clauses verified from immutable source."""
    try:
        printed_name = "Wail (1/Day)"
        if printed_name not in monster.action_names:
            return []
        source = source_sections_2014(monster.source_actions).get(printed_name)
        if source is None:
            return []
        normalized = " ".join(source.replace("’", "'").split())
        match = _WAIL_SOURCE.fullmatch(normalized)
        if match is None:
            return []
        radius = int(match["radius"])
        dc = int(match["dc"])
        count = int(match["count"])
        size = int(match["size"])
        if radius % 5 or count < 1:
            return []
        return [SaveCapabilityDefinition(
            id="wail", name=printed_name, save_ability="constitution", dc=dc,
            range_ft=radius, area=AreaTargeting(
                shape="emanation", origin="self", radius_ft=radius,
            ),
            target_scope="all-other-creatures",
            requires_target_hearing=True,
            excluded_target_creature_types=["construct", "undead"],
            prohibited_environment_context_id="sunlight",
            damage=DiceSpec(count=count, size=size),
            damage_type=DamageType.PSYCHIC,
            failure_sets_zero_hp=True,
            damage_only_on_success=True,
            resource_id="wail", resource_cost=1,
            animation="wail",
        )]
    except Exception:
        logger.exception("Failed 2014 source-verified asymmetric save binding for %s.", monster.id)
        raise
