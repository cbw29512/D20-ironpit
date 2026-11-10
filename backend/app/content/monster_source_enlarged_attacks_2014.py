"""Source-correct 2014 enlarged dice, using existing replacement damage effects."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_source_enlarge_2014 import source_enlarge_actions_2014

logger = logging.getLogger(__name__)
_ATTACK = re.compile(
    r"^(?P<kind>Melee(?: or Ranged)? Weapon Attack): "
    r"\+(?P<hit>\d+) to hit, reach (?P<reach>\d+) ft\."
    r"(?: or range (?P<normal>\d+)/(?P<long>\d+) ft\.)?, one target\. "
    r"Hit: (?P<avg>\d+) \((?P<count>\d+)d(?P<die>\d+) \+ (?P<flat>\d+)\) "
    r"(?P<type>[a-z]+) damage, or (?P<bigavg>\d+) "
    r"\((?P<bigcount>\d+)d(?P<bigdie>\d+) \+ (?P<bigflat>\d+)\) "
    r"(?P=type) damage while enlarged\.$", re.IGNORECASE,
)


def _printed_profile(monster: SourceMonster2014, attack: SourceAttack2014):
    try:
        if not source_enlarge_actions_2014(monster):
            return None
        text = source_sections_2014(monster.source_actions).get(attack.name, "")
        match = _ATTACK.fullmatch(" ".join(text.split()))
        if match is None:
            return None
        p = match.groupdict()
        original = attack.damage
        if (
            int(p["hit"]) != attack.attack_bonus
            or int(p["reach"]) != attack.reach_ft
            or (int(p["avg"]), int(p["count"]), int(p["die"]), int(p["flat"]),
                p["type"].casefold()) !=
            (original.average, original.dice_count, original.dice_size,
                original.bonus, str(original.type).casefold())
            or int(p["bigcount"]) != original.dice_count * 2
            or int(p["bigdie"]) != original.dice_size
            or int(p["bigflat"]) != original.bonus
            or int(p["bigavg"]) !=
                int((original.dice_count * 2 * (original.dice_size + 1) / 2)
                    + original.bonus)
            or attack.conditional_damage
            or attack.on_hit_damage
            or attack.on_hit_save_effect
            or attack.control_effect
            or attack.ongoing_damage_effect
        ):
            return None
        is_dual = p["kind"].casefold() == "melee or ranged weapon attack"
        if is_dual != (p["normal"] is not None and p["long"] is not None):
            return None
        if is_dual:
            if (attack.normal_range_ft, attack.long_range_ft) != (
                int(p["normal"]), int(p["long"]),
            ):
                return None
        elif attack.normal_range_ft is not None or attack.long_range_ft is not None:
            return None
        return p
    except Exception:
        logger.exception("2014 enlarged weapon source proof failed: %s / %s.",
                         monster.name, attack.name)
        raise


def source_completed_enlarged_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Bind alternate dice only while the generic timed 'enlarge' effect is live."""
    try:
        if attack.source_complete:
            return attack
        printed = _printed_profile(monster, attack)
        if printed is None:
            return attack
        return attack.model_copy(update={
            "source_complete": True,
            "conditional_damage": [{
                "trigger": "attacker_active_effect",
                "required_effect_id": "enlarge",
                "mode": "replace_weapon",
                "dice_count": int(printed["bigcount"]),
                "dice_size": int(printed["bigdie"]),
                "damage_bonus": int(printed["bigflat"]),
                "damage_type": printed["type"].casefold(),
            }],
        })
    except Exception:
        logger.exception("2014 enlarged weapon compilation failed: %s / %s.",
                         monster.name, attack.name)
        raise


def source_enlarged_dual_range_attacks_2014(
    monster: SourceMonster2014,
) -> list[SourceAttack2014]:
    """Preserve the printed 'Melee or Ranged' attack as a ranged option too."""
    try:
        output: list[SourceAttack2014] = []
        for attack in monster.attacks:
            printed = _printed_profile(monster, attack)
            if printed is None or printed["kind"].casefold() != "melee or ranged weapon attack":
                continue
            completed = source_completed_enlarged_attack_2014(monster, attack)
            output.append(completed.model_copy(update={
                "id": f"{attack.id}-ranged", "kind": "ranged",
            }))
        return output
    except Exception:
        logger.exception("2014 dual-range enlarged weapon compilation failed for %s.",
                         monster.name)
        raise
