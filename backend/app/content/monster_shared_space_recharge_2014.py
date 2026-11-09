"""Source-only 2014 audit of rechargeable same-occupied-square saves.

This is an INCOMPLETE ability contract: it identifies the common source
header, but never claims that grapples, forced movement, collision riders,
capacity, repeat damage, or other outcomes have been implemented.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)
_RECHARGE = re.compile(
    r"^(?P<name>.+?) \(Recharge (?P<minimum>[1-6])(?:–|-)6\)$",
    re.IGNORECASE,
)
_OCCUPIED_SAVE = re.compile(
    r"^Each creature in the (?P<owner>[^.]+?)'s space must make a "
    r"DC (?P<dc>\d+) (?P<ability>Strength|Dexterity|Constitution|"
    r"Intelligence|Wisdom|Charisma) saving throw\. (?P<remainder>.+)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SharedSpaceRechargeHeader:
    action_id: str
    source_name: str
    recharge_minimum: int
    save_dc: int
    save_ability: str
    # Preserve the unresolved outcome text for a future full-source proof.
    unbound_outcomes: str


def source_shared_space_recharge_headers_2014(
    monster: SourceMonster2014,
) -> tuple[SharedSpaceRechargeHeader, ...]:
    """Find reusable source headers without certifying incomplete Actions."""
    try:
        sections = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        found: list[SharedSpaceRechargeHeader] = []
        for heading, body in sections.items():
            if heading not in monster.action_names:
                continue
            recharge = _RECHARGE.fullmatch(heading)
            if recharge is None:
                continue
            label = action_label_2014(heading)
            ids = [
                action_id for action_id in monster.action_recharges
                if action_id.replace("-", " ").casefold() == label
            ]
            if len(ids) != 1:
                continue
            action_id = ids[0]
            minimum = int(recharge["minimum"])
            if monster.action_recharges[action_id] != minimum:
                continue
            match = _OCCUPIED_SAVE.fullmatch(" ".join(body.split()))
            if match is None:
                continue
            found.append(SharedSpaceRechargeHeader(
                action_id=action_id, source_name=recharge["name"],
                recharge_minimum=minimum,
                save_dc=int(match["dc"]), save_ability=match["ability"].casefold(),
                unbound_outcomes=match["remainder"],
            ))
        return tuple(found)
    except Exception:
        logger.exception(
            "Shared-space Recharge source-header audit failed for %s.", monster.id,
        )
        raise
