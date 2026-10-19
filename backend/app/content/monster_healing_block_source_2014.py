"""Complete an already-modeled on-hit poison/healing block from its full source."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)
_POISON = re.compile(
    r"Melee Weapon Attack: \+(?P<hit>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one creature\. Hit: (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+) "
    r"\+ (?P<bonus>\d+)\) (?P<type>\w+) damage, and the target must succeed "
    r"on a DC (?P<dc>\d+) (?P<ability>Constitution) saving throw or be poisoned "
    r"for (?P<minutes>\d+) minute(?:s)?\. While poisoned in this way, the target "
    r"can't regain hit points\. The target can repeat the saving throw at the "
    r"end of each of its turns, ending the effect on itself on a success\.",
    re.IGNORECASE,
)


def source_completed_healing_block_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Return a copy only when all attack facts and the exact linked rider agree."""
    try:
        if attack.source_complete or attack.kind != "melee":
            return attack
        text = source_sections_2014(monster.source_actions).get(attack.name, "")
        match = _POISON.fullmatch(text)
        if match is None:
            return attack
        expected_damage = dict(
            average=int(match["average"]), dice_count=int(match["count"]),
            dice_size=int(match["size"]), bonus=int(match["bonus"]),
            type=match["type"].casefold(),
        )
        expected_effect = dict(
            save_ability=match["ability"].casefold(), dc=int(match["dc"]),
            condition_id="poisoned", duration_rounds=int(match["minutes"]) * 10,
            repeat_save_timing="target_turn_end", cannot_regain_hit_points=True,
        )
        if (attack.attack_bonus != int(match["hit"])
                or attack.reach_ft != int(match["reach"])
                or attack.damage.model_dump() != expected_damage
                or attack.on_hit_save_effect != expected_effect):
            return attack
        if (attack.on_hit_damage or attack.conditional_damage or attack.conditional_attack_advantage
                or attack.control_effect is not None or attack.ongoing_damage_effect is not None
                or attack.on_hit_contested_movement is not None or attack.resource_id is not None
                or attack.breakable_restraint is not None or attack.charge_profile is not None
                or attack.normal_range_ft is not None or attack.long_range_ft is not None
                or attack.forbid_target_grappled_by_self or attack.grapple_target_policy != "normal"):
            return attack
        return attack.model_copy(update={"source_complete": True})
    except Exception:
        logger.exception("Failed healing-block source proof for %s/%s.", monster.id, attack.id)
        raise
