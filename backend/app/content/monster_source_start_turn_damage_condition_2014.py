"""Strict source proof for an on-hit timed condition with start-turn damage."""
from __future__ import annotations

import logging
import re

from pydantic import BaseModel, Field

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


class StartTurnDamageConditionProof2014(BaseModel):
    """Immutable source parameters for a failed-save timed condition."""

    condition_id: str = Field(min_length=1)
    save_ability: str = Field(min_length=1)
    dc: int = Field(ge=1, le=40)
    cannot_regain_hit_points: bool = False
    start_of_turn_damage_dice_count: int = Field(ge=1, le=40)
    start_of_turn_damage_dice_size: int = Field(ge=2, le=100)
    start_of_turn_damage_type: str = Field(min_length=1)
    repeat_save_timing: str = Field(min_length=1)


_PATTERN = re.compile(
    r"Melee Weapon Attack: \+(?P<to_hit>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<base_avg>\d+) \((?P<base_n>\d+)d(?P<base_s>\d+) "
    r"\+ (?P<base_bonus>\d+)\) (?P<base_type>\w+) damage\. "
    r"The target must succeed on a DC (?P<dc>\d+) Constitution saving throw "
    r"or become poisoned\. While poisoned in this way, the target can't regain "
    r"hit points, and it takes (?P<tick_avg>\d+) \((?P<tick_n>\d+)d"
    r"(?P<tick_s>\d+)\) (?P<tick_type>\w+) damage at the start of each of its turns\. "
    r"The poisoned target can repeat the saving throw at the end of each of its turns, "
    r"ending the effect on itself on a success\.",
    re.IGNORECASE,
)


def source_proven_start_turn_damage_condition_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> StartTurnDamageConditionProof2014 | None:
    """Return generic timed-condition parameters only for a complete exact source match."""
    try:
        if attack.source_complete or attack.kind != "melee":
            return None
        if (
            attack.on_hit_save_effect is not None
            or attack.control_effect is not None
            or attack.ongoing_damage_effect is not None
            or attack.conditional_damage
            or attack.conditional_attack_advantage
            or attack.on_hit_ability_score_reduction is not None
            or attack.on_hit_contested_movement is not None
            or attack.resource_id is not None
            or attack.breakable_restraint is not None
            or attack.charge_profile is not None
            or attack.forbid_target_grappled_by_self
            or attack.grapple_target_policy != "normal"
            or attack.on_hit_damage
        ):
            return None
        printed = source_sections_2014(monster.source_actions).get(attack.name, "")
        normalized = " ".join(printed.replace("’", "'").split())
        match = _PATTERN.fullmatch(normalized)
        if match is None:
            return None

        values = {
            key: int(value) if value.isdigit() else value.lower()
            for key, value in match.groupdict().items()
        }
        base = attack.damage
        if (
            values["to_hit"] != attack.attack_bonus
            or values["reach"] != attack.reach_ft
            or (
                base.average,
                base.dice_count,
                base.dice_size,
                base.bonus,
                base.type,
            )
            != (
                values["base_avg"],
                values["base_n"],
                values["base_s"],
                values["base_bonus"],
                values["base_type"],
            )
            or values["tick_avg"]
            != values["tick_n"] * (values["tick_s"] + 1) // 2
        ):
            return None

        return StartTurnDamageConditionProof2014(
            condition_id="poisoned",
            save_ability="constitution",
            dc=values["dc"],
            cannot_regain_hit_points=True,
            start_of_turn_damage_dice_count=values["tick_n"],
            start_of_turn_damage_dice_size=values["tick_s"],
            start_of_turn_damage_type=values["tick_type"],
            repeat_save_timing="target_turn_end",
        )
    except Exception:
        logger.exception(
            "Failed to prove start-turn damage condition source for %s/%s.",
            monster.id,
            attack.id,
        )
        raise
