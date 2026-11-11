"""Source-prove end-turn recurring weapon-hit effects across 2014 cards."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.recurring_damage import OnHitRecurringDamage

logger = logging.getLogger(__name__)

# This is source grammar, not a name/monster-specific combat resolver.
_IGNITION = re.compile(
    r"if the target is a creature(?: or a flammable object)?, it ignites\. "
    r"until a creature takes an action to douse the fire, the target takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<sides>\d+)\) (?P<type>\w+) "
    r"damage at the end of each of its turns\.",
    flags=re.IGNORECASE,
)


def source_end_turn_recurring_damage_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> OnHitRecurringDamage | None:
    """Return only fully source-proven hit/tick dice; douse range stays blocked."""
    try:
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "").strip()
        match = _IGNITION.search(section)
        if match is None or match.end() != len(section):
            return None
        # The ordinary attack parser owns its hit/damage fields; the recurring
        # clause must actually be attached to the same printed hit paragraph.
        if "Hit:" not in section[:match.start()]:
            return None
        count, sides, average = (
            int(match["count"]), int(match["sides"]), int(match["average"])
        )
        if not (1 <= count <= 40 and 2 <= sides <= 100):
            return None
        if average != count * (sides + 1) // 2:
            return None
        return OnHitRecurringDamage(
            effect_id="burning", dice_count=count, dice_size=sides,
            damage_type=match["type"].lower(),
            removal_action_ids=["douse-fire"],
        )
    except Exception:
        logger.exception("2014 recurring hit-effect source proof failed for %s.", monster.id)
        raise

# Match the *entire* base hit paragraph before the independently proven burn.
_BASE_HIT = re.compile(
    r"Melee Weapon Attack: \\+(?P<bonus>\\d+) to hit, reach (?P<reach>\\d+) ft\\., "
    r"one target\\. Hit: (?P<average>\\d+) \\((?P<count>\\d+)d(?P<sides>\\d+)\\) "
    r"(?P<type>[a-z]+) damage\\. ",
    re.IGNORECASE,
)


def source_completed_end_turn_ignition_attack_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Prove all base attack fields and the recurring rider, without a douse AI."""
    try:
        proof = source_end_turn_recurring_damage_2014(monster, attack)
        if proof is None or attack.kind != "melee":
            return attack
        if any((
            attack.on_hit_save_effect, attack.control_effect,
            attack.on_hit_damage, attack.conditional_damage,
            attack.on_hit_ability_score_reduction,
            attack.on_hit_contested_movement,
            attack.resource_id, attack.breakable_restraint, attack.charge_profile,
        )):
            return attack
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "").strip()
        ignition = _IGNITION.search(section)
        if ignition is None or ignition.end() != len(section):
            return attack
        base = _BASE_HIT.fullmatch(section[:ignition.start()])
        if base is None:
            return attack
        fields = (
            int(base["bonus"]), int(base["reach"]), int(base["average"]),
            int(base["count"]), int(base["sides"]), base["type"].lower(),
        )
        actual = (
            attack.attack_bonus, attack.reach_ft, attack.damage.average,
            attack.damage.dice_count, attack.damage.dice_size, attack.damage.type,
        )
        if fields != actual or attack.damage.bonus != 0:
            return attack
        expected = fields[3] * (fields[4] + 1) // 2
        if fields[2] != expected:
            return attack
        return attack.model_copy(update={"source_complete": True})
    except Exception:
        logger.exception("End-turn ignition attack completion failed: %s/%s",
                         monster.id, attack.id)
        raise
