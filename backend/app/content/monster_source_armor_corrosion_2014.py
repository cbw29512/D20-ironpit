"""Source-accurate 2014 on-hit armor corrosion as an engine-independent profile.

This file does not admit an incomplete attack or change runtime damage.
Admission requires source-owned routing to both Python and browser hit hooks.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

_PSEUDOPOD_CORROSION = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<base_avg>\d+) \((?P<base_n>\d+)d(?P<base_s>\d+) "
    r"\+ (?P<base_plus>\d+)\) (?P<base_type>\w+) damage plus "
    r"(?P<acid_avg>\d+) \((?P<acid_n>\d+)d(?P<acid_s>\d+)\) "
    r"(?P<acid_type>\w+) damage, and if the target is wearing nonmagical "
    r"metal armor, its armor is partly corroded and takes a permanent and "
    r"cumulative −1 penalty to the AC it offers\. The armor is destroyed "
    r"if the penalty reduces its AC to 10\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OnHitArmorCorrosion2014:
    source_name: str
    required_armor_material: str = "metal"
    requires_nonmagical_armor: bool = True
    penalty_per_hit: int = 1
    destroys_at_armor_ac: int = 10
    fight_only: bool = True


def source_on_hit_armor_corrosion_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> OnHitArmorCorrosion2014 | None:
    """Full printed effect and both pre-existing damage components must agree."""
    if attack.source_complete or attack.kind != "melee":
        return None
    if (attack.control_effect is not None or attack.on_hit_save_effect is not None
            or attack.ongoing_damage_effect is not None
            or attack.conditional_damage or len(attack.on_hit_damage) != 1):
        return None
    section = source_sections_2014(
        monster.source_actions, include_continuations=True,
    ).get(attack.name, "")
    match = _PSEUDOPOD_CORROSION.fullmatch(section)
    if match is None:
        return None
    data = match.groupdict()
    base = attack.damage
    if (int(data["bonus"]) != attack.attack_bonus
            or int(data["reach"]) != attack.reach_ft
            or (int(data["base_avg"]), int(data["base_n"]),
                int(data["base_s"]), int(data["base_plus"]),
                data["base_type"].lower()) != (
                base.average, base.dice_count, base.dice_size,
                base.bonus, base.type)):
        return None
    extra = attack.on_hit_damage[0]
    if extra != {
        "average": int(data["acid_avg"]), "dice_count": int(data["acid_n"]),
        "dice_size": int(data["acid_s"]), "bonus": 0,
        "type": data["acid_type"].lower(),
    }:
        return None
    return OnHitArmorCorrosion2014(source_name=attack.name)
