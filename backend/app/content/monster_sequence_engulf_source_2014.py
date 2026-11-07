"""Strict 2014 printed double-hit + grapple + containment source proof.

A declarative sequence can apply any named container effect when two ordinary
attacks hit one eligible target. Combat never dispatches on a creature name.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_TWO_HITS = re.compile(
    r"The (?P<owner>[a-z][a-z -]+) makes two (?P<attack>[a-z][a-z -]+) attacks\. "
    r"If both attacks hit a (?P<size>Small|Medium|Large) or smaller target, "
    r"the target is grappled \(escape DC (?P<grapple_dc>\d+)\), and the "
    r"(?P=owner) uses its (?P<action>[a-z][a-z -]+) on it\.",
    re.I,
)
_CONTAIN = re.compile(
    r"The (?P<owner>[a-z][a-z -]+) engulfs a (?P<size>Small|Medium|Large) "
    r"or smaller creature grappled by it\. The engulfed target is blinded, "
    r"restrained, and unable to breathe, and it must succeed on a DC "
    r"(?P<save_dc>\d+) (?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"saving throw at the start of each of the (?P<short>[a-z]+)'s turns "
    r"or take (?P<average>\d+) \((?P<count>\d+)d(?P<die>\d+) \+ "
    r"(?P<bonus>\d+)\) (?P<damage_type>[a-z]+) damage\. "
    r"If the (?P=short) moves, the engulfed target moves with it\. "
    r"The (?P=short) can have only one creature engulfed at a time\.",
    re.I,
)


@dataclass(frozen=True)
class SequenceContainmentSource2014:
    source_name: str
    attack_id: str
    max_target_size: CreatureSize
    grapple_dc: int
    required_sequence_hits: int
    damage_dice_count: int
    damage_dice_size: int
    damage_bonus: int
    damage_type: str
    start_turn_save_dc: int
    start_turn_save_ability: str


def source_sequence_containment_2014(
    monster: SourceMonster2014,
) -> SequenceContainmentSource2014 | None:
    """Require one complete printed sequence and an exact matching typed card."""
    try:
        if len(monster.swallow_actions) != 1:
            return None
        sections = source_sections_2014(
            monster.source_actions, include_continuations=True,
        )
        multi = _TWO_HITS.fullmatch(sections.get("Multiattack", ""))
        if multi is None:
            return None
        rule = _CONTAIN.fullmatch(sections.get(multi["action"], ""))
        if (
            rule is None or rule["owner"].casefold() != multi["owner"].casefold()
            or rule["short"].casefold() != multi["owner"].split()[-1].casefold()
            or rule["size"].casefold() != multi["size"].casefold()
            or multi["attack"].casefold() not in {"slam", "bite", "claw"}
            or len(monster.attacks) != 1 or monster.multiattack_slots
        ):
            return None
        attack = monster.attacks[0]
        if (
            not attack.source_complete or attack.kind != "melee"
            or attack.name.casefold() != multi["attack"].casefold()
            or any((attack.on_hit_damage, attack.conditional_damage,
                    attack.control_effect, attack.on_hit_save_effect))
        ):
            return None
        count, die, bonus = int(rule["count"]), int(rule["die"]), int(rule["bonus"])
        if int(rule["average"]) != count * (die + 1) // 2 + bonus:
            return None
        data = monster.swallow_actions[0]
        required = {
            "id", "name", "attack_id", "max_target_size",
            "requires_existing_grapple", "damage_dice_count",
            "damage_dice_size", "damage_bonus", "damage_type",
            "max_swallowed", "start_turn_save_dc", "start_turn_save_ability",
            "source_death_release", "exit_movement_ft", "exit_prone",
        }
        if not isinstance(data, dict) or set(data) != required:
            return None
        matches = {
            "id": re.sub(r"[^a-z0-9]+", "-", multi["action"].casefold()).strip("-"),
            "name": multi["action"],
            "attack_id": None,  # Action follows two ordinary attacks; it isn't a Bite.
            "max_target_size": multi["size"].casefold(),
            "requires_existing_grapple": True,
            "damage_dice_count": count, "damage_dice_size": die,
            "damage_bonus": bonus, "damage_type": rule["damage_type"].casefold(),
            "max_swallowed": 1, "start_turn_save_dc": int(rule["save_dc"]),
            "start_turn_save_ability": rule["ability"].casefold(),
            "source_death_release": "immediate",
            "exit_movement_ft": 0, "exit_prone": False,
        }
        if data != matches:
            return None
        if int(multi["grapple_dc"]) <= 0 or int(multi["grapple_dc"]) > 40:
            return None
        return SequenceContainmentSource2014(
            multi["action"], attack.id, CreatureSize(multi["size"].casefold()),
            int(multi["grapple_dc"]), 2, count, die, bonus,
            rule["damage_type"].casefold(), int(rule["save_dc"]),
            rule["ability"].casefold(),
        )
    except Exception:
        logger.exception("Failed source proof for two-hit containment.")
        raise
