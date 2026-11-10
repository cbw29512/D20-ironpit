"""Strict source-proof for attacks whose critical hits triple damage dice.

This is source decoding, not a runtime monster dispatch.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_TRIPLE_CRITICAL = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+) \+ (?P<flat>\d+)\) "
    r"(?P<type>slashing|piercing|bludgeoning) damage plus "
    r"(?P<extra_average>\d+) \((?P<extra_count>\d+)d(?P<extra_size>\d+)\) "
    r"(?P<extra_type>fire|cold|lightning|acid|poison|necrotic|radiant|force|psychic|thunder) "
    r"damage\. If the (?P<owner>[A-Za-z'-]+) scores a critical hit, "
    r"it rolls damage dice three times, instead of twice\.",
    re.IGNORECASE,
)


def source_completed_critical_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Compile the complete typed hit and printed critical multiplier only."""
    try:
        if attack.source_complete or attack.kind != "melee":
            return attack
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        match = _TRIPLE_CRITICAL.fullmatch(printed)
        if match is None:
            return attack
        p = match.groupdict()
        base = attack.damage
        extra = {
            "average": int(p["extra_average"]),
            "dice_count": int(p["extra_count"]),
            "dice_size": int(p["extra_size"]),
            "bonus": 0,
            "type": p["extra_type"].casefold(),
        }
        if (
            int(p["bonus"]) != attack.attack_bonus
            or int(p["reach"]) != attack.reach_ft
            or base.average != int(p["average"])
            or base.dice_count != int(p["count"])
            or base.dice_size != int(p["size"])
            or base.bonus != int(p["flat"])
            or base.type != p["type"].casefold()
            or attack.on_hit_damage != [extra]
            or attack.on_hit_save_effect is not None
            or attack.on_hit_contested_movement is not None
            or base.average != (base.dice_count * (base.dice_size + 1)) // 2 + base.bonus
            or extra["average"] != extra["dice_count"] * (extra["dice_size"] + 1) // 2
        ):
            return attack
        return attack.model_copy(update={
            "source_complete": True, "critical_dice_multiplier": 3,
        })
    except Exception:
        logger.exception("Could not certify source-triple-critical hit for %s.", monster.id)
        raise
