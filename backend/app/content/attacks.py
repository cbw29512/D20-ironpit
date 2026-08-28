from __future__ import annotations

import logging

from app.content.equipment import build_longsword, build_scimitar, build_shortbow
from app.content.thrown_weapons import build_handaxe_throw
from app.domain.models import ConditionalDamage, DamageType, WeaponAttack

logger = logging.getLogger(__name__)


def _goblin_advantage_damage(damage_type: DamageType) -> list[ConditionalDamage]:
    try:
        return [
            ConditionalDamage(
                trigger="attack_advantage",
                dice_count=1,
                dice_size=4,
                damage_type=damage_type,
            )
        ]
    except Exception as exc:
        logger.exception("Failed to build Goblin advantage damage.")
        raise RuntimeError("Goblin conditional damage could not be created.") from exc


def build_fighter_longsword_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="aldric-longsword",
            weapon=build_longsword(),
            attack_bonus=5,
            ability_damage_modifier=3,
        )
    except Exception as exc:
        logger.exception("Failed to build Fighter longsword attack profile.")
        raise RuntimeError("Fighter longsword attack could not be created.") from exc


def build_fighter_handaxe_throw() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="aldric-handaxe-throw",
            weapon=build_handaxe_throw(),
            attack_bonus=5,
            ability_damage_modifier=3,
            open_tactic_eligible=False,
        )
    except Exception as exc:
        logger.exception("Failed to build Fighter thrown handaxe attack profile.")
        raise RuntimeError("Fighter thrown handaxe attack could not be created.") from exc


def build_goblin_scimitar_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="goblin-scimitar",
            weapon=build_scimitar(),
            attack_bonus=4,
            ability_damage_modifier=2,
            conditional_damage=_goblin_advantage_damage(DamageType.SLASHING),
        )
    except Exception as exc:
        logger.exception("Failed to build Goblin scimitar attack profile.")
        raise RuntimeError("Goblin scimitar attack could not be created.") from exc


def build_goblin_shortbow_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="goblin-shortbow",
            weapon=build_shortbow(),
            attack_bonus=4,
            ability_damage_modifier=2,
            conditional_damage=_goblin_advantage_damage(DamageType.PIERCING),
        )
    except Exception as exc:
        logger.exception("Failed to build Goblin shortbow attack profile.")
        raise RuntimeError("Goblin shortbow attack could not be created.") from exc
