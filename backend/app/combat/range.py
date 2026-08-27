from __future__ import annotations

import logging

from app.combat.rolls import resolve_roll_mode
from app.domain.models import RollMode, Weapon, WeaponAttackKind

logger = logging.getLogger(__name__)


def resolve_attack_roll_mode(
    weapon: Weapon,
    distance_ft: int,
    advantage_sources: int = 0,
    other_disadvantage_sources: int = 0,
    close_enemy_active: bool = True,
) -> RollMode:
    """Validate weapon range and combine range-related Advantage/Disadvantage sources."""
    try:
        if distance_ft < 0:
            raise ValueError("Distance cannot be negative.")

        disadvantage_sources = other_disadvantage_sources
        if weapon.attack_kind is WeaponAttackKind.MELEE:
            if distance_ft > weapon.reach_ft:
                raise ValueError(f"{weapon.name} target is outside melee reach.")
        else:
            if weapon.normal_range_ft is None or weapon.long_range_ft is None:
                raise ValueError(f"{weapon.name} is missing ranged weapon distances.")
            if distance_ft > weapon.long_range_ft:
                raise ValueError(f"{weapon.name} target is beyond long range.")
            if distance_ft > weapon.normal_range_ft:
                disadvantage_sources += 1
            if distance_ft <= 5 and close_enemy_active:
                disadvantage_sources += 1

        return resolve_roll_mode(
            advantage_sources=advantage_sources,
            disadvantage_sources=disadvantage_sources,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve attack range for %s.", weapon.name)
        raise RuntimeError("Attack range could not be resolved.") from exc
