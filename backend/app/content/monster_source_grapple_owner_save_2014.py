"""Compile source-proven held-target saving-throw Actions without monster-ID dispatch."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_grapple_capacity_2014 import source_completed_limited_grapple_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)

_HELD_SAVE = re.compile(
    r"^The (?P<actor>[\w -]+) slams creatures grappled by it into each other or a solid surface\. "
    r"Each creature must succeed on a DC (?P<dc>\d+) Constitution saving throw or take "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+) \+ (?P<bonus>\d+)\) "
    r"bludgeoning damage and be stunned until the end of the (?P=actor)'s next turn\. "
    r"On a successful save, the target takes half the bludgeoning damage and isn't stunned\.$",
    re.IGNORECASE,
)


def source_proven_grapple_owner_saves_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Source-owned DC/dice/target cap and existing source-grapple targeting semantics."""
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        result: list[SaveCapabilityDefinition] = []
        for name, body in sections.items():
            match = _HELD_SAVE.fullmatch(" ".join(body.split()))
            if match is None:
                continue
            # The attack that creates the link owns its printed limit and reach.
            # No synthetic Slam distance or target count is introduced.
            holders = []
            for attack in monster.attacks:
                bound = source_completed_limited_grapple_2014(monster, attack)
                control = bound.control_effect
                if isinstance(control, dict) and control.get("max_active_grapples"):
                    holders.append((bound.reach_ft, control["max_active_grapples"]))
            if len(holders) != 1:
                continue
            reach, capacity = holders[0]
            count, size, bonus = (int(match[key]) for key in ("count", "size", "bonus"))
            average = int(match["average"])
            if average != (count * (size + 1) // 2 + bonus):
                continue
            result.append(SaveCapabilityDefinition(
                id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"),
                name=name, save_ability="constitution", dc=int(match["dc"]),
                range_ft=reach, max_targets=capacity,
                target_scope="all-other-creatures",
                requires_target_grappled_by_source=True,
                damage=DiceSpec(count=count, size=size, bonus=bonus),
                damage_type=DamageType.BLUDGEONING, success_damage="half",
                effect_tags=["stunned"],
                failed_save_timed_effect=FailedSaveTimedEffect(
                    effect_id="stunned", duration_rounds=1,
                    expiry_timing="source_turn_end",
                ),
            ))
        return result
    except Exception:
        logger.exception("2014 source-owned grapple save proof failed for %s", monster.id)
        raise
