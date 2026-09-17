from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def _attack(level: int, scores: AbilityScores, weapon: Weapon, attack_id: str) -> WeaponAttack:
    strength = scores.modifier("strength")
    return WeaponAttack(
        id=attack_id,
        weapon=weapon,
        attack_bonus=proficiency_bonus(level) + strength,
        damage_bonus=strength,
        attack_ability="strength",
        attack_ability_modifier=strength,
    )


def build_longsword_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    try:
        weapon = build_weapon("longsword").model_copy(update={"mastery_property": None})
        return _attack(level, scores, weapon, "aurelia-2014-longsword")
    except Exception:
        logger.exception("Failed to build Aurelia's 2014 longsword attack at level %s", level)
        raise


def build_javelin_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    try:
        weapon = Weapon(
            id="javelin",
            name="Javelin",
            attack_kind=WeaponAttackKind.RANGED,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.PIERCING,
            animation="projectile",
            normal_range_ft=30,
            long_range_ft=120,
            projectile="javelin",
            mastery_property=None,
        )
        return _attack(level, scores, weapon, "aurelia-2014-javelin")
    except Exception:
        logger.exception("Failed to build Aurelia's 2014 javelin attack at level %s", level)
        raise


def build_extra_attack(level: int) -> AttackActionDefinition | None:
    try:
        if level < 5:
            return None
        choices = ["aurelia-2014-longsword", "aurelia-2014-javelin"]
        return AttackActionDefinition(
            id="extra-attack",
            name="Extra Attack",
            slots=[
                AttackActionSlot(attack_ids=choices),
                AttackActionSlot(attack_ids=choices),
            ],
            is_attack_action=True,
        )
    except Exception:
        logger.exception("Failed to build Aurelia's 2014 Extra Attack at level %s", level)
        raise
