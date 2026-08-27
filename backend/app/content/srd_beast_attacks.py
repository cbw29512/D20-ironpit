from __future__ import annotations

import logging

from app.domain.models import (
    AttackEffect,
    ConditionType,
    DamageType,
    SizeCategory,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)

logger = logging.getLogger(__name__)


def build_wolf_bite_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="wolf-bite",
            weapon=Weapon(
                id="bite",
                name="Bite",
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=1,
                dice_size=6,
                damage_type=DamageType.PIERCING,
                animation="bite",
                reach_ft=5,
            ),
            attack_bonus=4,
            damage_bonus=2,
            on_hit_effects=[AttackEffect(
                id="wolf-bite-prone",
                effect_type="condition",
                condition=ConditionType.PRONE,
                max_target_size=SizeCategory.MEDIUM,
            )],
        )
    except Exception as exc:
        logger.exception("Failed to build Wolf Bite attack.")
        raise RuntimeError("Wolf Bite attack could not be created.") from exc


def build_giant_crab_claw_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="giant-crab-claw",
            weapon=Weapon(
                id="claw",
                name="Claw",
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=1,
                dice_size=6,
                damage_type=DamageType.BLUDGEONING,
                animation="claw",
                reach_ft=5,
            ),
            attack_bonus=3,
            damage_bonus=1,
            on_hit_effects=[AttackEffect(
                id="giant-crab-claw-grapple",
                effect_type="condition",
                condition=ConditionType.GRAPPLED,
                escape_dc=11,
                max_target_size=SizeCategory.MEDIUM,
            )],
        )
    except Exception as exc:
        logger.exception("Failed to build Giant Crab Claw attack.")
        raise RuntimeError("Giant Crab Claw attack could not be created.") from exc


def build_lion_rend_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="lion-rend",
            weapon=Weapon(
                id="rend",
                name="Rend",
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=1,
                dice_size=8,
                damage_type=DamageType.SLASHING,
                animation="claw",
                reach_ft=5,
            ),
            attack_bonus=5,
            damage_bonus=3,
        )
    except Exception as exc:
        logger.exception("Failed to build Lion Rend attack.")
        raise RuntimeError("Lion Rend attack could not be created.") from exc
