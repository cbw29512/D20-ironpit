"""Derive a reusable ignite-on-hit effect directly from printed 2014 card text."""
from __future__ import annotations

from dataclasses import dataclass
import re

from app.content.monster_source_sections_2014 import source_sections_2014

_IGNITES = re.compile(
    r"if the target is a creature(?: or a flammable object)?, it ignites\. "
    r"until a creature takes an action to douse the fire, the target takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) (?P<type>\w+) "
    r"damage at the end of each of its turns\.", re.I,
)


@dataclass(frozen=True)
class IgniteOnHitSource2014:
    attack_id: str
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str


def source_ignite_on_hit_2014(monster, attack):
    """Only a complete matching attack paragraph may supply this effect."""
    text = source_sections_2014(
        monster.source_actions, include_continuations=True
    ).get(attack.name, "")
    match = _IGNITES.search(text)
    if match is None or not attack.source_complete:
        return None
    count, sides, average = (
        int(match["count"]), int(match["sides"]), int(match["average"])
    )
    if not (1 <= count <= 40 and 2 <= sides <= 100):
        return None
    if average != count * (sides + 1) // 2:
        return None
    return IgniteOnHitSource2014(
        attack_id=attack.id, damage_dice_count=count,
        damage_dice_size=sides, damage_type=match["type"].casefold(),
    )
