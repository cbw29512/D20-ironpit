"""Fail-closed 2014 source proof for a destructible, two-save barrier Action.

This module audits immutable source data only. It does not install an Action,
select placement, or claim that the monster is ready for combat.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_EXPECTED = (
    "the devil magically forms an opaque wall of ice on a solid surface it "
    "can see within 60 feet of it. the wall is 1 foot thick and up to 30 "
    "feet long and 10 feet high, or it's a hemispherical dome up to 20 feet "
    "in diameter. when the wall appears, each creature in its space is "
    "pushed out of it by the shortest route. the creature chooses which side "
    "of the wall to end up on, unless the creature is incapacitated. the "
    "creature then makes a dc 17 dexterity saving throw, taking 35 (10d6) "
    "cold damage on a failed save, or half as much damage on a successful one. "
    "the wall lasts for 1 minute or until the devil is incapacitated or dies. "
    "the wall can be damaged and breached; each 10-foot section has ac 5, "
    "30 hit points, vulnerability to fire damage, and immunity to acid, cold, "
    "necrotic, poison, and psychic damage. if a section is destroyed, it "
    "leaves behind a sheet of frigid air in the space the wall occupied. "
    "whenever a creature finishes moving through the frigid air on a turn, "
    "willingly or otherwise, the creature must make a dc 17 constitution "
    "saving throw, taking 17 (5d6) cold damage on a failed save, or half "
    "as much damage on a successful one. the frigid air dissipates when "
    "the rest of the wall vanishes."
)


@dataclass(frozen=True)
class SourceBarrierParameters:
    source_name: str
    action_id: str
    recharge_minimum: int
    cast_range_ft: int
    max_wall_length_ft: int
    wall_height_ft: int
    dome_diameter_ft: int
    section_length_ft: int
    section_ac: int
    section_hp: int
    duration_rounds: int
    fire_vulnerable: bool
    damage_immunities: tuple[str, ...]
    creation_save_ability: str
    creation_save_dc: int
    creation_damage_dice: str
    cross_destroyed_section_save_ability: str
    cross_destroyed_section_dc: int
    cross_destroyed_section_damage_dice: str
    ends_when_source_incapacitated: bool
    ends_when_source_dead: bool


def source_barrier_parameters_2014(monster: SourceMonster2014) -> SourceBarrierParameters | None:
    """Accept only an exact printed 2014 barrier text and matching Recharge id."""
    try:
        sections = source_sections_2014(monster.source_actions, include_continuations=True)
        for heading, printed in sections.items():
            if not re.fullmatch(r".+ \(Recharge 6\)", heading):
                continue
            normalized = " ".join(
                printed.casefold()
                .replace("\u00ad", "").replace("‑", "-").replace("–", "-")
                .replace("’", "'").split()
            )
            if normalized != _EXPECTED:
                continue
            action_ids = [
                identifier for identifier, minimum in monster.action_recharges.items()
                if minimum == 6 and identifier.replace("-", " ").casefold()
                == heading.split(" (Recharge", 1)[0].casefold()
            ]
            if len(action_ids) != 1:
                continue
            return SourceBarrierParameters(
                source_name=heading.split(" (Recharge", 1)[0],
                action_id=action_ids[0], recharge_minimum=6,
                cast_range_ft=60, max_wall_length_ft=30, wall_height_ft=10,
                dome_diameter_ft=20, section_length_ft=10, section_ac=5,
                section_hp=30, duration_rounds=10, fire_vulnerable=True,
                damage_immunities=("acid", "cold", "necrotic", "poison", "psychic"),
                creation_save_ability="dexterity", creation_save_dc=17,
                creation_damage_dice="10d6",
                cross_destroyed_section_save_ability="constitution",
                cross_destroyed_section_dc=17,
                cross_destroyed_section_damage_dice="5d6",
                ends_when_source_incapacitated=True,
                ends_when_source_dead=True,
            )
        return None
    except Exception:
        logger.exception("2014 printed barrier proof failed for %s", monster.id)
        raise
