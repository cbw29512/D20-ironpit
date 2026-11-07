"""Source-verified on-hit, start-of-target-turn recurring typed damage.

The source owns the hit, dice and timing. Generic timed effects own state,
damage and the legal Action removal. No guessed helper douse range is used.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.recurring_damage import OnHitRecurringDamage

logger = logging.getLogger(__name__)

# Whole printed attack, not a fragment of the ignition sentence.
_PRINTED = re.compile(
    r"Melee Weapon Attack: \+(?P<bonus>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+) "
    r"\+ (?P<flat>\d+)\) (?P<type>\w+) damage\. "
    r"If the target is a creature or a flammable object, it ignites\. "
    r"Until a creature takes an action to douse the fire, the target takes "
    r"(?P<burn_avg>\d+) \((?P<burn_count>\d+)d(?P<burn_size>\d+)\) "
    r"(?P<burn_type>\w+) damage at the start of each of its turns\.",
    re.IGNORECASE,
)


def source_start_turn_recurring_damage_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> OnHitRecurringDamage | None:
    """Fail closed unless complete immutable text and typed data agree."""
    try:
        if attack.kind != "melee" or not isinstance(attack.ongoing_damage_effect, dict):
            return None
        if (
            attack.on_hit_save_effect is not None or attack.control_effect is not None
            or attack.on_hit_damage or attack.conditional_damage
            or attack.on_hit_ability_score_reduction is not None
            or attack.on_hit_contested_movement is not None
            or attack.resource_id is not None or attack.breakable_restraint is not None
            or attack.charge_profile is not None
        ):
            return None
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        match = _PRINTED.fullmatch(printed)
        if match is None:
            return None
        fields = {key: int(value) if value.isdecimal() else value.lower()
                  for key, value in match.groupdict().items()}
        attack_values = (
            attack.attack_bonus, attack.reach_ft, attack.damage.average,
            attack.damage.dice_count, attack.damage.dice_size,
            attack.damage.bonus, attack.damage.type,
        )
        printed_values = (
            fields["bonus"], fields["reach"], fields["average"],
            fields["count"], fields["size"], fields["flat"], fields["type"],
        )
        if attack_values != printed_values:
            return None
        if fields["average"] != fields["count"] * (fields["size"] + 1) // 2 + fields["flat"]:
            return None
        if fields["burn_avg"] != fields["burn_count"] * (fields["burn_size"] + 1) // 2:
            return None
        raw = attack.ongoing_damage_effect
        required = {
            "id", "name", "dice_count", "dice_size", "damage_bonus", "damage_type",
            "apply_on", "tick_timing", "action_removable", "action_removal_range_ft",
        }
        if (
            set(raw) != required or not isinstance(raw["id"], str)
            or not raw["id"].strip() or not isinstance(raw["name"], str)
            or not raw["name"].strip()
            or raw["dice_count"] != fields["burn_count"]
            or raw["dice_size"] != fields["burn_size"]
            or raw["damage_bonus"] != 0 or raw["damage_type"] != fields["burn_type"]
            or raw["apply_on"] != "hit" or raw["tick_timing"] != "target_turn_start"
            or raw["action_removable"] is not True
            or not isinstance(raw["action_removal_range_ft"], int)
            or raw["action_removal_range_ft"] < 0
        ):
            return None
        # A structured helper range is not printed by the source. The universal
        # self-douse action is valid, but helper reach must remain unsupported.
        return OnHitRecurringDamage(
            effect_id="burning", dice_count=fields["burn_count"],
            dice_size=fields["burn_size"], damage_type=fields["burn_type"],
            tick_timing="target_turn_start", removal_action_ids=["douse-fire"],
        )
    except Exception:
        logger.exception("Failed source proof for a start-turn recurring hit: %s/%s.",
                         monster.id, attack.id)
        raise
