from __future__ import annotations

import logging

from app.content.rogue_equipment import build_shortbow, build_shortsword
from app.domain.models import ConditionalDamage, DamageType, WeaponAttack

logger = logging.getLogger(__name__)


def _sneak_attack() -> list[ConditionalDamage]:
    return [
        ConditionalDamage(
            trigger="attack_advantage",
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.PIERCING,
        )
    ]


def _attack(attack_id: str, weapon) -> WeaponAttack:
    try:
        return WeaponAttack(
            id=attack_id,
            weapon=weapon,
            attack_bonus=5,
            damage_bonus=3,
            conditional_damage=_sneak_attack(),
        )
    except Exception as exc:
        logger.exception("Failed to build Rogue attack %s.", attack_id)
        raise RuntimeError(f"Rogue attack {attack_id} could not be created.") from exc


def build_mara_shortsword_attack() -> WeaponAttack:
    return _attack("mara-shortsword", build_shortsword())


def build_mara_shortbow_attack() -> WeaponAttack:
    return _attack("mara-shortbow", build_shortbow())
