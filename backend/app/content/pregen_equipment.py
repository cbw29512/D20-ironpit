from __future__ import annotations

import logging

from app.domain.models import DamageType, VisualLoadout, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def build_greataxe() -> Weapon:
    try:
        return Weapon(
            id="greataxe",
            name="Greataxe",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=12,
            damage_type=DamageType.SLASHING,
            animation="heavy-slash",
            reach_ft=5,
            mastery_property="Cleave",
        )
    except Exception as exc:
        logger.exception("Failed to build greataxe content record.")
        raise RuntimeError("Greataxe content could not be created.") from exc


def build_heavy_fighter_visual_loadout() -> VisualLoadout:
    try:
        return VisualLoadout(
            armor="chain-mail",
            main_hand="greataxe",
            body_style="humanoid",
        )
    except Exception as exc:
        logger.exception("Failed to build heavy Fighter visual loadout.")
        raise RuntimeError("Heavy Fighter visual loadout could not be created.") from exc
