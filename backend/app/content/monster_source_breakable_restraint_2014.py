"""Strict source proof for a rechargeable, ranged hit with a breakable snare.

Schema: immutable attack owns hit bonus, 30/60-style range, resource and
breakable-object data. State: the universal condition runtime owns Restrained
and a fresh object-durability record for each successful hit.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_HEADING = re.compile(r"(.+?) \(Recharge ([1-6])(?:–|-)6\)")
_PRINTED = re.compile(
    r"Ranged Weapon Attack: \+(?P<bonus>\d+) to hit, range "
    r"(?P<normal>\d+)/(?P<long>\d+) ft\., one (?P<size>Large or smaller )?"
    r"creature\. Hit: The (?P<target>target|creature) is restrained by "
    r"webbing\. As an action, the restrained (?P=target) can make a DC "
    r"(?P<escape>\d+) Strength check, "
    r"(?:bursting the webbing|escaping from the webbing) on a success\. "
    r"(?:The webbing can also be attacked and destroyed "
    r"\(AC (?P<ac1>\d+); hp (?P<hp1>\d+); vulnerability to fire damage; "
    r"immunity to bludgeoning, poison, and psychic damage\)\."
    r"|The effect also ends if the webbing is destroyed\. "
    r"The webbing has AC (?P<ac2>\d+), (?P<hp2>\d+) hit points, "
    r"vulnerability to fire damage, and immunity to bludgeoning, "
    r"poison, and psychic damage\.)"
)


@dataclass(frozen=True)
class RangedBreakableRestraint2014:
    resource_id: str
    recharge_minimum: int
    escape_dc: int
    max_target_size: CreatureSize | None
    object_ac: int
    object_hp: int
    damage_vulnerabilities: tuple[str, ...]
    damage_immunities: tuple[str, ...]


def source_recharge_breakable_restraint_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> RangedBreakableRestraint2014 | None:
    """Match the whole printed Action AND typed source values; no creature ID."""
    try:
        if not attack.source_complete or attack.kind != "ranged":
            return None
        if attack.resource_id != attack.id or not attack.breakable_restraint:
            return None
        if (attack.damage.dice_count != 0 or attack.damage.bonus != 0
                or attack.damage.type is not None or attack.on_hit_damage
                or attack.on_hit_save_effect or attack.control_effect):
            return None
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        for heading, source in sections.items():
            h = _HEADING.fullmatch(heading)
            if h is None or h[1].casefold() != attack.name.casefold():
                continue
            minimum = int(h[2])
            if monster.action_recharges.get(attack.resource_id) != minimum:
                return None
            match = _PRINTED.fullmatch(source)
            if match is None:
                return None
            values = match.groupdict()
            ac = int(values["ac1"] or values["ac2"])
            hp = int(values["hp1"] or values["hp2"])
            max_size = CreatureSize.LARGE if values["size"] else None
            expected = {
                "condition_id": "restrained",
                "escape_ability": "strength",
                "escape_dc": int(values["escape"]),
                "object_ac": ac,
                "object_hp": hp,
                "damage_vulnerabilities": ["fire"],
                "damage_immunities": ["bludgeoning", "poison", "psychic"],
            }
            if max_size is not None:
                expected["max_target_size"] = "large"
            if (attack.breakable_restraint != expected
                    or attack.attack_bonus != int(values["bonus"])
                    or attack.normal_range_ft != int(values["normal"])
                    or attack.long_range_ft != int(values["long"])
                    or ac < 1 or hp < 1):
                return None
            return RangedBreakableRestraint2014(
                attack.id, minimum, expected["escape_dc"], max_size, ac, hp,
                ("fire",), ("bludgeoning", "poison", "psychic"),
            )
        return None
    except Exception:
        logger.exception("Failed 2014 rechargeable breakable-restraint proof for %s.", attack.id)
        raise
