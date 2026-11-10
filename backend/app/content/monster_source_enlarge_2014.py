"""Source-proven 2014 enlargement composed from universal timed-buff mechanics.

The printed Action supplies duration, size, save/check eligibility and recharge.
Source-attached alternative weapon profiles use generic effect-linked damage.
No monster identity is referenced by engine behavior or source-binding dispatch.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.combatants import ResourceDefinition
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.size import CreatureSize
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_HEADING = "Enlarge (Recharges after a Short or Long Rest)"
_ENLARGE = re.compile(
    r"For 1 minute, the (?P<owner>[a-z][a-z'-]*) magically increases in size, "
    r"along with anything it is wearing or carrying\. While enlarged, the "
    r"(?P=owner) is Large, doubles its damage dice on Strength-based weapon "
    r"attacks \(included in the attacks\), and makes Strength checks and Strength "
    r"saving throws with advantage\. If the (?P=owner) lacks the room to become "
    r"Large, it attains the maximum size possible in the space available\.",
    re.IGNORECASE,
)
_WEAPON = re.compile(
    r"(?P<mode>Melee(?: or Ranged)?) Weapon Attack: "
    r"\+(?P<attack_bonus>\d+) to hit, reach (?P<reach>\d+) ft\."
    r"(?: or range (?P<near>\d+)/(?P<far>\d+) ft\.)?, one target\. "
    r"Hit: (?P<normal_average>\d+) \((?P<count>\d+)d(?P<size>\d+) \+ (?P<bonus>\d+)\) "
    r"(?P<type>[a-z]+) damage, or (?P<large_average>\d+) "
    r"\((?P<large_count>\d+)d(?P<large_size>\d+) \+ (?P<large_bonus>\d+)\) "
    r"(?P<large_type>[a-z]+) damage while enlarged\.",
    re.IGNORECASE,
)


def _valid_source(monster: SourceMonster2014) -> bool:
    if _HEADING not in monster.action_names:
        return False
    printed = source_sections_2014(monster.source_actions, include_continuations=True).get(_HEADING, "")
    return bool(_ENLARGE.fullmatch(printed))


def source_enlarge_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind only complete printed Enlarge text to one generic self-buff."""
    try:
        if not _valid_source(monster):
            return []
        return [TimedSelfBuffAction(
            id="enlarge", name="Enlarge", action_cost="action",
            resource_id="enlarge", duration_rounds=10,
            expiry_timing="source_turn_start", magical_effect=True,
            size_override=CreatureSize.LARGE,
            ability_check_advantage_abilities=["strength"],
            saving_throw_advantage_grants=[SavingThrowAdvantageGrant(
                source_id="enlarge-strength-save", source_name="Enlarge",
                abilities=["strength"],
            )],
            animation="buff", priority=75,
        )]
    except Exception:
        logger.exception("Could not compile source-owned 2014 Enlarge for %s.", monster.id)
        raise


def source_enlarge_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    try:
        return [
            ResourceDefinition(id="enlarge", name="Enlarge", max_uses=1)
            for _ in source_enlarge_action_2014(monster)
        ]
    except Exception:
        logger.exception("Could not bind Enlarge rest recharge for %s.", monster.id)
        raise


def source_enlarge_weapon_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """Return an immutable upgrade only for fully matched printed weapon modes."""
    try:
        if not source_enlarge_action_2014(monster) or attack.source_complete:
            return attack
        if attack.kind != "melee" or attack.attack_ability != "strength":
            return attack
        source = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        match = _WEAPON.fullmatch(source)
        if match is None:
            return attack
        m = match.groupdict()
        dice = attack.damage
        if (
            int(m["attack_bonus"]) != attack.attack_bonus
            or int(m["reach"]) != attack.reach_ft
            or (int(m["near"]) if m["near"] else None) != attack.normal_range_ft
            or (int(m["far"]) if m["far"] else None) != attack.long_range_ft
            or m["type"].lower() != dice.type
            or m["large_type"].lower() != dice.type
            or (int(m["normal_average"]), int(m["count"]), int(m["size"]), int(m["bonus"]))
               != (dice.average, dice.dice_count, dice.dice_size, dice.bonus)
            or (int(m["large_average"]), int(m["large_count"]), int(m["large_size"]),
                int(m["large_bonus"])) != (
                dice.dice_count * (dice.dice_size + 1) + dice.bonus,
                dice.dice_count * 2, dice.dice_size, dice.bonus,
            )
        ):
            return attack
        source_effect = {
            "trigger": "attacker_active_effect", "required_effect_id": "enlarge",
            "mode": "replace_weapon", "dice_count": int(m["large_count"]),
            "dice_size": int(m["large_size"]), "damage_bonus": int(m["large_bonus"]),
            "damage_type": dice.type,
        }
        if attack.conditional_damage:
            return attack  # Do not double-count an existing printed rider.
        return attack.model_copy(update={
            "source_complete": True, "conditional_damage": [source_effect],
        })
    except Exception:
        logger.exception("Could not bind enlarged attack %s for %s.", attack.id, monster.id)
        raise


def source_enlarge_ranged_weapon_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> bool:
    """Source-proven dual-mode weapon gets a second, ranged attack card."""
    try:
        ready = source_enlarge_weapon_2014(monster, attack)
        if not ready.source_complete or ready.kind != "melee":
            return False
        clause = source_sections_2014(monster.source_actions).get(ready.name, "")
        match = _WEAPON.fullmatch(clause)
        return bool(match and match.group("mode").casefold() == "melee or ranged")
    except Exception:
        logger.exception("Could not classify printed ranged alternative for %s.", attack.id)
        raise
