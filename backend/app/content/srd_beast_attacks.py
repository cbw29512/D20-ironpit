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
            on_hit_effects=[
                AttackEffect(
                    id="wolf-bite-prone",
                    effect_type="condition",
                    condition=ConditionType.PRONE,
                    max_target_size=SizeCategory.MEDIUM,
                )
            ],
        )
    except Exception as exc:
        logger.exception("Failed to build Wolf Bite attack.")
        raise RuntimeError("Wolf Bite attack could not be created.") from exc
