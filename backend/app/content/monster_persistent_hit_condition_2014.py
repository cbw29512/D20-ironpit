"""Prove an incomplete ranged hit's existing damage and persistent Poisoned save.

This binds printed parameters to existing shared effects; it never resolves combat.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_PRINTED = re.compile(
    r"Ranged Weapon Attack: (?P<hit>[+-]?\d+) to hit, range "
    r"(?P<normal>\d+)/(?P<long>\d+) ft\., one target\. Hit: "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+) \+ (?P<bonus>\d+)\) "
    r"(?P<type>\w+) damage plus (?P<extra_average>\d+) "
    r"\((?P<extra_count>\d+)d(?P<extra_size>\d+)\) (?P<extra_type>\w+) damage, "
    r"and the target must succeed on a DC (?P<dc>\d+) "
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"saving throw or be poisoned\. The poison lasts until it is removed by "
    r"the lesser restoration spell or similar magic\.", re.I,
)


def source_completed_persistent_hit_condition_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Fail closed unless the entire attack paragraph and parsed damage agree."""
    try:
        if attack.source_complete or attack.kind != "ranged":
            return attack
        if any(value is not None for value in (
                attack.on_hit_save_effect, attack.control_effect, attack.ongoing_damage_effect,
                attack.on_hit_contested_movement, attack.charge_profile,
                attack.resource_id, attack.breakable_restraint)):
            return attack
        if any((attack.conditional_damage, attack.conditional_attack_advantage,
                attack.forbid_target_grappled_by_self, attack.grapple_target_policy != "normal")):
            return attack
        text = source_sections_2014(monster.source_actions).get(attack.name, "")
        match = _PRINTED.fullmatch(text)
        if match is None:
            return attack
        values = match.groupdict()
        base = {"average": int(values["average"]), "dice_count": int(values["count"]),
                "dice_size": int(values["size"]), "bonus": int(values["bonus"]),
                "type": values["type"].lower()}
        extra = {"average": int(values["extra_average"]), "dice_count": int(values["extra_count"]),
                 "dice_size": int(values["extra_size"]), "bonus": 0,
                 "type": values["extra_type"].lower()}
        if (int(values["hit"]) != attack.attack_bonus
                or int(values["normal"]) != attack.normal_range_ft
                or int(values["long"]) != attack.long_range_ft
                or base != attack.damage.model_dump()
                or attack.on_hit_damage != [extra]
                or base["type"] not in DamageType._value2member_map_
                or extra["type"] not in DamageType._value2member_map_
                or not 1 <= int(values["dc"]) <= 40):
            return attack
        # No duration/repeat fields means the existing persistent condition, not a timer.
        return attack.model_copy(update={"source_complete": True, "on_hit_save_effect": {
            "condition_id": "poisoned", "dc": int(values["dc"]),
            "save_ability": values["ability"].lower(),
        }})
    except Exception:
        logger.exception("Failed persistent hit-condition source proof for %s / %s.", monster.id, attack.id)
        raise
