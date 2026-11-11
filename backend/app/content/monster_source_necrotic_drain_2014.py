"""Semantic 327-card proof for the printed Bite drain family, without runtime names."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.on_hit_typed_drain import AttackTargetQualification, OnHitTypedDrain
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_SOURCE = re.compile(
    r"Melee Weapon Attack: \+(?P<hit>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one willing creature, or a creature that is grappled by the (?P<actor>[a-z]+), "
    r"incapacitated, or restrained\. Hit: (?P<base_avg>\d+) "
    r"\((?P<base_n>\d+)d(?P<base_s>\d+) \+ (?P<base_bonus>\d+)\) piercing damage "
    r"plus (?P<extra_avg>\d+) \((?P<extra_n>\d+)d(?P<extra_s>\d+)\) necrotic damage\. "
    r"The target's hit point maximum is reduced by an amount equal to the necrotic "
    r"damage taken, and the (?P=actor) regains hit points equal to that amount\. "
    r"The reduction lasts until the target finishes a long rest\. "
    r"The target dies if this effect reduces its hit point maximum to 0\."
    r"(?: A humanoid slain in this way and then buried in the ground rises "
    r"the following night as a vampire spawn under the (?P=actor)'s control\.)?",
    re.IGNORECASE,
)

def source_proven_typed_drain_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> tuple[AttackTargetQualification, OnHitTypedDrain] | None:
    """Only whole-section 2014 damage, target and life-transfer proof counts."""
    try:
        if attack.kind != "melee":
            return None
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        match = _SOURCE.fullmatch(section)
        if match is None:
            return None
        p = {key: int(value) for key, value in match.groupdict().items()
             if key not in {"actor"} and value is not None}
        base = attack.damage
        if (
            (attack.attack_bonus, attack.reach_ft) != (p["hit"], p["reach"])
            or (base.average, base.dice_count, base.dice_size, base.bonus, base.type)
               != (p["base_avg"], p["base_n"], p["base_s"], p["base_bonus"], "piercing")
            or attack.on_hit_damage != [{
                "average": p["extra_avg"], "dice_count": p["extra_n"],
                "dice_size": p["extra_s"], "bonus": 0, "type": "necrotic",
            }]
            or attack.on_hit_save_effect is not None
            or attack.control_effect is not None
            or attack.conditional_damage
        ):
            return None
        return (
            AttackTargetQualification(
                any_of=["source_grappled", "incapacitated", "restrained", "willing"],
            ),
            OnHitTypedDrain(
                damage_type=DamageType.NECROTIC,
                reduce_target_maximum_hp=True,
                heal_attacker=True,
                zero_maximum_hp_kills=True,
            ),
        )
    except Exception:
        logger.exception("Failed to prove source-owned typed hit drain for %s/%s.", monster.id, attack.id)
        raise
