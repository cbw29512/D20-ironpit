"""Source-proven on-hit condition lasting until magical condition removal.

Do not implement the creature's printed attack again. Complete its source
data so the universal attack/save/condition/removal engine can run it.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Reject unreviewed additional damage, effects, or different save/expiry terms.
_RANGED_POISON_UNTIL_CURED = re.compile(
    r"Ranged Weapon Attack: \\+(?P<to_hit>\\d+) to hit, range "
    r"(?P<normal>\\d+)/(?P<long>\\d+) ft\\., one target\\. Hit: "
    r"(?P<base_avg>\\d+) \\((?P<base_n>\\d+)d(?P<base_s>\\d+) \\+ "
    r"(?P<base_bonus>\\d+)\\) (?P<base_type>\\w+) damage plus "
    r"(?P<extra_avg>\\d+) \\((?P<extra_n>\\d+)d(?P<extra_s>\\d+)\\) "
    r"(?P<extra_type>\\w+) damage, and the target must succeed on a DC "
    r"(?P<dc>\\d+) Constitution saving throw or be poisoned\\. "
    r"The poison lasts until it is removed by the lesser restoration spell "
    r"or similar magic\\.",
    re.IGNORECASE,
)


def source_completed_magic_cured_condition_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Prove the entire printed ranged hit and attach an indefinite condition."""
    try:
        if attack.source_complete or attack.kind != "ranged":
            return attack
        if (attack.on_hit_save_effect is not None or attack.control_effect
                or attack.ongoing_damage_effect or attack.conditional_damage
                or len(attack.on_hit_damage) != 1):
            return attack
        printed = source_sections_2014(monster.source_actions).get(attack.name, "")
        match = _RANGED_POISON_UNTIL_CURED.fullmatch(printed)
        if match is None:
            return attack
        values = {key: int(value) if value.isdigit() else value.lower()
                  for key, value in match.groupdict().items()}
        base = attack.damage
        base_signature = (base.average, base.dice_count, base.dice_size,
                          base.bonus, base.type)
        printed_signature = (values["base_avg"], values["base_n"],
                             values["base_s"], values["base_bonus"],
                             values["base_type"])
        expected_extra = {
            "average": values["extra_avg"], "dice_count": values["extra_n"],
            "dice_size": values["extra_s"], "bonus": 0,
            "type": values["extra_type"],
        }
        if (values["to_hit"] != attack.attack_bonus
                or (values["normal"], values["long"]) !=
                    (attack.normal_range_ft, attack.long_range_ft)
                or base_signature != printed_signature
                or attack.on_hit_damage != [expected_extra]):
            return attack
        return attack.model_copy(update={
            "source_complete": True,
            "on_hit_save_effect": {
                "save_ability": "constitution",
                "dc": values["dc"],
                "condition_id": "poisoned",
                # None: ends only through the usual magical condition removal.
                # Neither a 10-round timer nor a repeat save is printed.
            },
        })
    except Exception:
        logger.exception("Source-proven magical-condition rider failed for %s/%s.",
                         monster.id, attack.id)
        raise
