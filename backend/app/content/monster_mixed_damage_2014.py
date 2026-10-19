"""Source-only correction for partial 2014 mixed-damage weapon attacks.

No monster-name dispatch, no combat rerouting, and no card mutations.
Equipment-destruction rider stays arena-neutral under Iron Pit rules.
"""
from __future__ import annotations

import html
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceDamage2014, SourceMonster2014
from app.content.monster_healing_block_source_2014 import source_completed_healing_block_2014
from app.domain.weapons_base import DamageType

_PATTERN = re.compile(
    r"(?P<name>[\w \-']+)\.\s*Melee Weapon Attack:\s*"
    r"\+(?P<hit>\d+) to hit,\s*reach (?P<reach>\d+) ft\.,\s*"
    r"one target\.\s*Hit:\s*"
    r"(?P<avg>\d+) \((?P<count>\d+)d(?P<size>\d+)\s*\+\s*(?P<bonus>\d+)\)"
    r" (?P<type>\w+) damage plus "
    r"(?P<extra_avg>\d+) \((?P<extra_count>\d+)d(?P<extra_size>\d+)\)"
    r" (?P<extra_type>\w+) damage\.",
    re.IGNORECASE,
)


def source_completed_mixed_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Upgrade a parser-incomplete attack only when both source hit dice are proven."""
    attack = source_completed_healing_block_2014(monster, attack)
    if attack.source_complete or attack.kind != "melee":
        return attack
    if attack.on_hit_save_effect or attack.control_effect or attack.ongoing_damage_effect:
        return attack
    source = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", monster.source_actions or "")).split())
    for match in _PATTERN.finditer(source):
        m = match.groupdict()
        if (m["name"].strip().lower() != attack.name.strip().lower()
                or int(m["hit"]) != attack.attack_bonus
                or int(m["reach"]) != attack.reach_ft):
            continue
        if (m["type"].lower() not in DamageType._value2member_map_
                or m["extra_type"].lower() not in DamageType._value2member_map_):
            continue
        base = SourceDamage2014(
            average=int(m["avg"]), dice_count=int(m["count"]), dice_size=int(m["size"]),
            bonus=int(m["bonus"]), type=m["type"].lower(),
        )
        extra = dict(
            average=int(m["extra_avg"]), dice_count=int(m["extra_count"]),
            dice_size=int(m["extra_size"]), bonus=0, type=m["extra_type"].lower(),
        )
        if attack.damage != base and attack.damage.model_dump() != extra:
            continue
        # A well-parsed existing second component must be reused, never doubled.
        if attack.on_hit_damage and attack.on_hit_damage != [extra]:
            continue
        # The full nonmagical-armor rider is explicitly neutral in the Pit.
        # Do not extend that exception to any unknown source riders.
        tail = source[match.end():]
        if ("In addition, nonmagical armor worn by the target" not in tail
                or "The armor is destroyed if the penalty reduces its AC to 10." not in tail):
            continue
        return attack.model_copy(update={
            "source_complete": True, "damage": base, "on_hit_damage": [extra],
        })
    return attack
