from __future__ import annotations

import logging

from app.domain.models import (
    Ability,
    AttackEffect,
    ConditionalDamage,
    ConditionExpiry,
    ConditionType,
    CreatureType,
    DamageType,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)

logger = logging.getLogger(__name__)


def build_ghoul_bite_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="ghoul-bite",
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
            conditional_damage=[ConditionalDamage(
                trigger="always",
                dice_count=1,
                dice_size=6,
                damage_type=DamageType.NECROTIC,
            )],
        )
    except Exception as exc:
        logger.exception("Failed to build Ghoul Bite.")
        raise RuntimeError("Ghoul Bite could not be created.") from exc


def build_ghoul_claw_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="ghoul-claw",
            weapon=Weapon(
                id="claw",
                name="Claw",
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=1,
                dice_size=4,
                damage_type=DamageType.SLASHING,
                animation="claw",
                reach_ft=5,
            ),
            attack_bonus=4,
            damage_bonus=2,
            on_hit_effects=[AttackEffect(
                id="ghoul-claw-paralysis",
                effect_type="save_condition",
                condition=ConditionType.PARALYZED,
                save_ability=Ability.CONSTITUTION,
                save_dc=10,
                expires_on=ConditionExpiry.TARGET_TURN_END,
                excluded_creature_types=[CreatureType.UNDEAD],
                excluded_creature_tags=["elf"],
            )],
        )
    except Exception as exc:
        logger.exception("Failed to build Ghoul Claw.")
        raise RuntimeError("Ghoul Claw could not be created.") from exc
