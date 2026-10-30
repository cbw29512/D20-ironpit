"""2014 source-verified grapple-then-Swallow actions, without name dispatch."""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_threshold_swallow_source_2014 import threshold_swallow_source_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_SIMPLE = re.compile(
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
    delivery_mode: str
    max_target_size: CreatureSize
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str
    max_swallowed: int
    exit_movement_ft: int
    regurgitation_damage_threshold: int | None = None
    regurgitation_save_ability: str | None = None
    regurgitation_save_dc: int | None = None
    regurgitation_range_ft: int | None = None
    regurgitation_all_swallowed: bool = False


def _simple_profile(monster: SourceMonster2014) -> GrappleSwallowSource2014 | None:
    try:
        if len(monster.swallow_actions) != 1:
            return None
        text = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get("Swallow", "")
        match = _SIMPLE.fullmatch(text)
        if match is None:
            return None
        groups = match.groupdict()
        actor = monster.name.split()[-1].lower()
        attack = next(
            (
                item for item in monster.attacks
                if item.name.casefold() == groups["attack"].casefold()
                and item.source_complete
            ),
            None,
        )
        if groups["actor"].lower() != actor or attack is None:
            return None

        data = monster.swallow_actions[0]
        size = CreatureSize(groups["size"].lower())
        count, sides = int(groups["count"]), int(groups["sides"])
        if int(groups["average"]) != count * (sides + 1) // 2:
            return None
        if not isinstance(data, dict) or not (
            data.get("id") == "swallow"
            and data.get("attack_id") == attack.id
            and data.get("max_target_size") == size.value
            and data.get("requires_existing_grapple") is True
            and data.get("damage_dice_count") == count
            and data.get("damage_dice_size") == sides
            and data.get("damage_bonus") == 0
            and data.get("damage_type") == groups["type"].lower()
            and data.get("max_swallowed") == 1
            and data.get("regurgitation_damage_threshold") is None
            and data.get("exit_movement_ft") == int(groups["exit"])
            and data.get("exit_prone") is True
        ):
            return None
        return GrappleSwallowSource2014(
            source_name="Swallow", attack_id=attack.id, delivery_mode="action_attack",
            max_target_size=size, damage_dice_count=count, damage_dice_size=sides,
            damage_type=groups["type"].lower(), max_swallowed=1,
            exit_movement_ft=int(groups["exit"]),
        )
    except Exception:
        logger.exception("Failed simple Swallow source proof for %s.", monster.id)
        raise


def source_grapple_swallow_2014(
    monster: SourceMonster2014,
) -> GrappleSwallowSource2014 | None:
    """Compile only fully proven simple or threshold-regurgitation Swallow text."""
    try:
        simple = _simple_profile(monster)
        if simple is not None:
            return simple
        threshold = threshold_swallow_source_2014(monster)
        if threshold is None:
            return None
        return GrappleSwallowSource2014(
            source_name="Swallow",
            attack_id=threshold.attack_id,
            delivery_mode=threshold.delivery_mode,
            max_target_size=threshold.max_target_size,
            damage_dice_count=threshold.damage_dice_count,
            damage_dice_size=threshold.damage_dice_size,
            damage_type=threshold.damage_type,
            max_swallowed=threshold.max_swallowed,
            exit_movement_ft=threshold.exit_movement_ft,
            regurgitation_damage_threshold=threshold.damage_threshold,
            regurgitation_save_ability="constitution",
            regurgitation_save_dc=threshold.save_dc,
            regurgitation_range_ft=threshold.range_ft,
            regurgitation_all_swallowed=threshold.all_swallowed,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Swallow source for %s.", monster.id)
        raise
