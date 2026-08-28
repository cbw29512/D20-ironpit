from __future__ import annotations

import logging

from app.content.equipment import build_scimitar
from app.content.monster_equipment import (
    build_axe_beak_beak,
    build_club,
    build_giant_lizard_bite,
    build_light_crossbow,
)
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
        logger.exception("Failed to build monster attack %s.", attack_id)
        raise RuntimeError(f"Monster attack {attack_id} could not be created.") from exc


def build_bandit_scimitar_attack() -> WeaponAttack:
    return _attack("bandit-scimitar", build_scimitar(), 3, 1)


def build_bandit_light_crossbow_attack() -> WeaponAttack:
    return _attack("bandit-light-crossbow", build_light_crossbow(), 3, 1)


def build_commoner_club_attack() -> WeaponAttack:
    return _attack("commoner-club", build_club(), 2, 0)


def build_axe_beak_attack() -> WeaponAttack:
    return _attack("axe-beak-beak", build_axe_beak_beak(), 4, 2)


def build_giant_lizard_attack() -> WeaponAttack:
    return _attack("giant-lizard-bite", build_giant_lizard_bite(), 4, 2)
