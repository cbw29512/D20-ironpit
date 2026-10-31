"""Source-proven limited-grapple appendages; applies to any matching 2014 card."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_HIT = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one (?:target|creature)\. Hit: (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+) \+ (?P<flat>\d+)\) "
    r"(?P<type>\w+) damage(?P<tail>.*)", re.I,
)
_EXTRA = re.compile(
    r" plus (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)\) "
    r"(?P<type>\w+) damage(?P<tail>.*)", re.I,
)
_LIMBS = re.compile(
    r"(?P<clause>.*) The [^.]+ has (?P<count>two|ten) "
    r"(?P<limbs>claws|pincers|tentacles), each of which can grapple "
    r"(?:only )?one target\.", re.I,
)
_GRAPPLES = (
    (re.compile(r", and the target is grappled \(escape DC (?P<dc>\d+)\)\."), False, None),
    (re.compile(r"\. If the target is a Medium or smaller creature, it is grappled "
                r"\(escape DC (?P<dc>\d+)\)\."), False, "medium"),
    (re.compile(r", and the target is grappled \(escape DC (?P<dc>\d+)\)\. "
                r"Until this grapple ends, the target is restrained\."), True, None),
    (re.compile(r"\. If the target is Medium or smaller, it is grappled "
                r"\(escape DC (?P<dc>\d+)\) and restrained until the grapple ends\."), True, "medium"),
)
_COUNTS = {"two": 2, "ten": 10}


def source_completed_limited_grapple_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Validate the entire on-hit clause, then add one generic source-owned limit."""
    try:
        if attack.kind != "melee" or not isinstance(attack.control_effect, dict):
            return attack
        if (attack.on_hit_save_effect is not None
                or attack.ongoing_damage_effect is not None
                or attack.conditional_damage
                or attack.on_hit_contested_movement is not None):
            return attack
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        hit = _HIT.fullmatch(section)
        if hit is None:
            return attack
        damage = attack.damage
        if (int(hit["bonus"]) != attack.attack_bonus
                or int(hit["reach"]) != attack.reach_ft
                or (int(hit["average"]), int(hit["count"]), int(hit["size"]),
                    int(hit["flat"]), hit["type"].lower())
                != (damage.average, damage.dice_count, damage.dice_size,
                    damage.bonus, damage.type)):
            return attack
        tail = hit["tail"]
        extra = _EXTRA.fullmatch(tail)
        if extra is not None:
            expected = [{
                "average": int(extra["average"]), "dice_count": int(extra["count"]),
                "dice_size": int(extra["size"]), "bonus": 0, "type": extra["type"].lower(),
            }]
            if attack.on_hit_damage != expected:
                return attack
            tail = extra["tail"]
        elif attack.on_hit_damage:
            return attack
        limb = _LIMBS.fullmatch(tail)
        if limb is None:
            return attack
        control = attack.control_effect
        if set(control) - {"grapple_escape_dc", "max_target_size", "restrains_while_grappled"}:
            return attack
        for pattern, restrains, size in _GRAPPLES:
            match = pattern.fullmatch(limb["clause"])
            if match is None:
                continue
            if (int(match["dc"]) != control.get("grapple_escape_dc")
                    or control.get("max_target_size") != size
                    or bool(control.get("restrains_while_grappled", False))
                    not in (restrains, False)):
                return attack
            value = {**control, "restrains_while_grappled": restrains,
                     "max_active_grapples": _COUNTS[limb["count"].lower()]}
            return attack.model_copy(update={"source_complete": True, "control_effect": value})
        return attack
    except Exception:
        logger.exception("Could not bind printed grapple capacity on %s/%s.", monster.id, attack.id)
        raise
