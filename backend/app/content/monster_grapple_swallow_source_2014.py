"""2014 source-verified grapple-then-Swallow actions, without name dispatch.

Parses the complete printed action and cross-checks its pinned capability row.
Recognition alone does not admit a creature; the universal state/turn/cover
engine must be bound and certified in both Python and browser first.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize


_GRAPPLE_SWALLOW = re.compile(
    r"The (?P<actor>[\w -]+) makes one (?P<attack>[\w -]+) attack against "
    r"a (?P<size>Small|Medium|Large) or smaller target it is grappling\. "
    r"If the attack hits, the target is swallowed, and the grapple ends\. "
    r"The swallowed target is blinded and restrained, it has total cover "
    r"against attacks and other effects outside the (?P=actor), and it takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) "
    r"(?P<type>\w+) damage at the start of each of the (?P=actor)'s turns\. "
    r"The (?P=actor) can have only one target swallowed at a time\. "
    r"If the (?P=actor) dies, a swallowed creature is no longer restrained "
    r"by it and can escape from the corpse using (?P<exit>\d+) feet of "
    r"movement, exiting prone\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GrappleSwallowSource2014:
    source_name: str
    attack_id: str
    max_target_size: CreatureSize
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str
    max_swallowed: int
    exit_movement_ft: int


def source_grapple_swallow_2014(
    monster: SourceMonster2014,
) -> GrappleSwallowSource2014 | None:
    """Only a full printed source match can expose the action to the engine."""
    if "Swallow" not in monster.action_names or len(monster.swallow_actions) != 1:
        return None
    text = source_sections_2014(
        monster.source_actions, include_continuations=True,
    ).get("Swallow", "")
    match = _GRAPPLE_SWALLOW.fullmatch(text)
    if match is None:
        return None
    groups = match.groupdict()
    actor = monster.name.split()[-1].lower()
    if groups["actor"].lower() != actor:
        return None
    attack = next((
        item for item in monster.attacks
        if item.name.casefold() == groups["attack"].casefold()
    ), None)
    if attack is None or not attack.source_complete:
        return None
    data = monster.swallow_actions[0]
    size = CreatureSize(groups["size"].lower())
    dice_count, dice_size = int(groups["count"]), int(groups["sides"])
    expected_average = dice_count * (dice_size + 1) // 2
    if int(groups["average"]) != expected_average:
        return None
    if not isinstance(data, dict) or not (
        data.get("id") == "swallow"
        and data.get("attack_id") == attack.id
        and data.get("max_target_size") == size.value
        and data.get("requires_existing_grapple") is True
        and data.get("damage_dice_count") == dice_count
        and data.get("damage_dice_size") == dice_size
        and data.get("damage_bonus") == 0
        and data.get("damage_type") == groups["type"].lower()
        and data.get("max_swallowed") == 1
        and data.get("regurgitation_damage_threshold") is None
        and data.get("exit_movement_ft") == int(groups["exit"])
        and data.get("exit_prone") is True
    ):
        return None
    if any(data.get(k) is not None for k in (
        "regurgitation_save_ability", "regurgitation_save_dc",
        "regurgitation_range_ft", "start_turn_save_dc",
    )):
        return None
    return GrappleSwallowSource2014(
        source_name="Swallow", attack_id=attack.id, max_target_size=size,
        damage_dice_count=dice_count, damage_dice_size=dice_size,
        damage_type=groups["type"].lower(),
        max_swallowed=1, exit_movement_ft=int(groups["exit"]),
    )
