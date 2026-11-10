"""Source-proof save-triggered pulls using the universal on-hit save and movement."""
from __future__ import annotations

import logging
import re
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_SAVE_PULL = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+) \+ (?P<flat>\d+)\) "
    r"(?P<type>slashing|piercing|bludgeoning) damage plus "
    r"(?P<extra_average>\d+) \((?P<extra_count>\d+)d(?P<extra_size>\d+)\) "
    r"(?P<extra_type>fire|cold|lightning|acid|poison|necrotic|radiant|force|psychic|thunder) "
    r"damage, and the target must succeed on a DC (?P<dc>\d+) "
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"saving throw or be pulled up to (?P<distance>\d+) feet toward the "
    r"(?P<owner>[A-Za-z'-]+)\.",
    re.IGNORECASE,
)

def source_completed_save_pull_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Compile printed DC/range/direction without changing pinned source cards."""
    try:
        if attack.source_complete or attack.kind != "melee":
            return attack
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        match = _SAVE_PULL.fullmatch(printed)
        if match is None:
            return attack
        p = match.groupdict()
        d = attack.damage
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
            or d.average != int(p["average"])
            or d.dice_count != int(p["count"])
            or d.dice_size != int(p["size"])
            or d.bonus != int(p["flat"])
            or d.type != p["type"].casefold()
            or attack.on_hit_damage != [extra]
            or attack.on_hit_save_effect is not None
            or attack.on_hit_contested_movement is not None
            or d.average != d.dice_count * (d.dice_size + 1) // 2 + d.bonus
            or extra["average"] != extra["dice_count"] * (extra["dice_size"] + 1) // 2
            or not 1 <= int(p["dc"]) <= 40
            or int(p["distance"]) <= 0
            or int(p["distance"]) % 5
        ):
            return attack
        return attack.model_copy(update={
            "source_complete": True,
            "on_hit_save_effect": {
                "save_ability": p["ability"].casefold(),
                "dc": int(p["dc"]),
                "failure_pull_ft": int(p["distance"]),
            },
        })
    except Exception:
        logger.exception("Source save-pull classification failed for %s.", monster.id)
        raise
