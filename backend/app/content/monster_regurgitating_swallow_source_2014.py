"""Source-validated regurgitation rules for the shared Swallow family.

This module proves immutable parameters only. It does not certify a card
until the universal Python/browser swallow lifecycle consumes the profile.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_PATTERN = re.compile(
    r"The (?P<actor>[\w -]+) makes one (?P<attack>[\w -]+) attack against "
    r"a (?P<size>Small|Medium|Large) or smaller target it is grappling\. "
    r"If the attack hits, the target is also swallowed, and the grapple ends\. "
    r"While swallowed, the target is blinded and restrained, it has total cover "
    r"against attacks and other effects outside the (?P=actor), and it takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) "
    r"(?P<type>\w+) damage at the start of each of the (?P=actor)'s turns\. "
    r"A (?P=actor) can have only one creature swallowed at a time\. "
    r"If the (?P=actor) takes (?P<threshold>\d+) damage or more on a single turn "
    r"from the swallowed creature, the (?P=actor) must succeed on a DC "
    r"(?P<dc>\d+) (?P<ability>Constitution) saving throw at the end of that turn "
    r"or regurgitate the creature, which falls prone in a space within "
    r"(?P<range>\d+) feet of the (?P=actor)\. "
    r"If the (?P=actor) dies, a swallowed creature is no longer restrained "
    r"by it and can escape from the corpse by using (?P<exit>\d+) feet "
    r"of movement, exiting prone\.",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RegurgitatingSwallowProof2014:
    source_name: str
    attack_id: str
    max_target_size: CreatureSize
    damage_dice_count: int
    damage_dice_size: int
    damage_type: str
    max_swallowed: int
    regurgitation_damage_threshold: int
    regurgitation_save_ability: str
    regurgitation_save_dc: int
    regurgitation_range_ft: int
    exit_movement_ft: int


def source_proven_regurgitating_swallow_2014(
    monster: SourceMonster2014,
) -> RegurgitatingSwallowProof2014 | None:
    """Reject any truncated or changed printed outcome and unresolved attack."""
    try:
        if "Swallow" not in monster.action_names:
            return None
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get("Swallow", "")
        match = _PATTERN.fullmatch(" ".join(printed.split()))
        if match is None:
            return None
        values = match.groupdict()
        if values["actor"].casefold() != monster.name.split()[-1].casefold():
            return None
        if len(monster.swallow_actions) != 1:
            return None
        attacks = [
            a for a in monster.attacks
            if a.name.casefold() == values["attack"].casefold()
            and a.source_complete and a.kind == "melee"
        ]
        if len(attacks) != 1:
            return None
        count, sides, average = (
            int(values["count"]), int(values["sides"]), int(values["average"]),
        )
        if not 1 <= count <= 40 or not 2 <= sides <= 100:
            return None
        if average != count * (sides + 1) // 2:
            return None
        threshold, dc, regurg_range, exit_ft = (
            int(values["threshold"]), int(values["dc"]),
            int(values["range"]), int(values["exit"]),
        )
        if not (threshold > 0 and 1 <= dc <= 40 and
                regurg_range > 0 and exit_ft > 0):
            return None
        if values["type"].casefold() not in {
            "acid", "cold", "fire", "lightning", "necrotic", "poison",
            "psychic", "radiant", "thunder", "force", "bludgeoning",
            "piercing", "slashing",
        }:
            return None
        data = monster.swallow_actions[0]
        if not isinstance(data, dict) or any((
            data.get("attack_id") != attacks[0].id,
            data.get("max_target_size") != values["size"].casefold(),
            data.get("requires_existing_grapple") is not True,
            data.get("damage_dice_count") != count,
            data.get("damage_dice_size") != sides,
            data.get("damage_type") != values["type"].casefold(),
            data.get("max_swallowed") != 1,
            data.get("regurgitation_damage_threshold") != threshold,
            data.get("regurgitation_save_dc") != dc,
            data.get("regurgitation_save_ability") != values["ability"].casefold(),
            data.get("regurgitation_range_ft") != regurg_range,
            data.get("exit_movement_ft") != exit_ft,
        )):
            return None
        return RegurgitatingSwallowProof2014(
            source_name="Swallow", attack_id=attacks[0].id,
            max_target_size=CreatureSize(values["size"].casefold()),
            damage_dice_count=count, damage_dice_size=sides,
            damage_type=values["type"].casefold(), max_swallowed=1,
            regurgitation_damage_threshold=threshold,
            regurgitation_save_ability=values["ability"].casefold(),
            regurgitation_save_dc=dc,
            regurgitation_range_ft=regurg_range,
            exit_movement_ft=exit_ft,
        )
    except Exception:
        logger.exception("Failed source proof for regurgitating Swallow: %s", monster.id)
        raise
