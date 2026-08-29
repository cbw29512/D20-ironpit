from __future__ import annotations

import logging

from app.content.pregen_equipment import build_greataxe, build_longbow
from app.domain.models import WeaponAttack

logger = logging.getLogger(__name__)


def _attack(attack_id: str, weapon, attack_bonus: int, damage_bonus: int) -> WeaponAttack:
    try:
        return WeaponAttack(
            id=attack_id,
            weapon=weapon,
            attack_bonus=attack_bonus,
            damage_bonus=damage_bonus,
        )
    except Exception as exc:
        logger.exception("Failed to build pregen attack %s.", attack_id)
        raise RuntimeError(f"Pregen attack {attack_id} could not be created.") from exc


def build_brom_greataxe_attack() -> WeaponAttack:
    return _attack("brom-greataxe", build_greataxe(), 5, 3)


def build_selene_longbow_attack() -> WeaponAttack:
    return _attack("selene-longbow", build_longbow(), 7, 3)
