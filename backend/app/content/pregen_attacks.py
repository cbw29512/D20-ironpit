from __future__ import annotations

import logging

from app.content.attack_bonus_rules import compile_weapon_attack_bonus
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
    weapon = build_greataxe()
    return _attack("brom-greataxe", weapon, 5, 3)


def build_selene_longbow_attack() -> WeaponAttack:
    weapon = build_longbow()
    attack_bonus = compile_weapon_attack_bonus(5, "Archery", weapon.attack_kind)
    return _attack("selene-longbow", weapon, attack_bonus, 3)
