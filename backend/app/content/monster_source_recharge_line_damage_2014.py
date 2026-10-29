"""Source-proof rechargeable line damage Actions from immutable 2014 cards."""
from __future__ import annotations

import logging
import re

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec

logger = logging.getLogger(__name__)

_RECHARGE = re.compile(
    r"^(?P<name>.+?) \(Recharge (?P<minimum>[1-6])(?:–|-)6\)$",
    flags=re.IGNORECASE,
)
_LINE_DAMAGE = re.compile(
    r"The (?P<subject>[^.]+?) exhales a line of (?P<energy>[^.]+?) that is "
    r"(?P<length>\d+) feet long and (?P<width>\d+) feet wide\. "
    r"Each creature in that line must make a DC (?P<dc>\d+) "
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"saving throw, taking (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)"
    r"(?: \+ (?P<bonus>\d+))?\) (?P<damage_type>[A-Za-z]+) damage on a "
    r"failed save, or half as much damage on a successful one\.",
    flags=re.IGNORECASE,
)


def source_proven_recharge_line_damage_2014(
    monster: SourceMonster2014,
) -> list[SaveCapabilityDefinition]:
    """Compile only complete printed line/save/half-damage Recharge Actions."""
    try:
        results: list[SaveCapabilityDefinition] = []
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        for heading, printed in sections.items():
            recharge = _RECHARGE.fullmatch(heading)
            if recharge is None:
                continue
            action_label = action_label_2014(heading)
            action_ids = [
                item for item in monster.action_recharges
                if item.replace("-", " ").casefold() == action_label
            ]
            if len(action_ids) != 1:
                continue
            action_id = action_ids[0]
            minimum = int(recharge["minimum"])
            if monster.action_recharges.get(action_id) != minimum:
                continue
            effect = _LINE_DAMAGE.fullmatch(" ".join(printed.split()))
            if effect is None:
                continue
            results.append(SaveCapabilityDefinition(
                id=action_id,
                name=recharge["name"].strip(),
                save_ability=effect["ability"].casefold(),
                dc=int(effect["dc"]),
                range_ft=int(effect["length"]),
                area={
                    "shape": "line",
                    "origin": "self",
                    "length_ft": int(effect["length"]),
                    "width_ft": int(effect["width"]),
                },
                damage=DiceSpec(
                    count=int(effect["count"]),
                    size=int(effect["size"]),
                    bonus=int(effect["bonus"] or 0),
                ),
                damage_type=effect["damage_type"].casefold(),
                success_damage="half",
                resource_id=action_id,
                resource_cost=1,
                animation="save-effect",
            ))
        return results
    except Exception:
        logger.exception(
            "Failed to bind source Recharge line damage for %s.", monster.name
        )
        raise
