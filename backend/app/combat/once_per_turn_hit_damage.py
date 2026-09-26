from __future__ import annotations

import logging

from app.content.monster_creature_types import base_creature_type
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.models import CombatantState, DamageType, WeaponAttack

logger = logging.getLogger(__name__)
BonusDamageSpec = tuple[str, int, int, int, DamageType]


def _qualified(
    rider: OncePerTurnWeaponHitDamageRider,
    target: CombatantState | None,
) -> bool:
    if rider.requires_target_below_max_hp:
        if target is None:
            raise ValueError(f"{rider.source_name} requires target state for its hit qualification.")
        if target.current_hp >= target.template.max_hp:
            return False
    if rider.target_creature_types:
        if target is None:
            raise ValueError(f"{rider.source_name} requires target state for its creature-type qualification.")
        target_type = base_creature_type(target.template.creature_type)
        if target_type not in rider.target_creature_types:
            return False
    return True


def _spec(
    rider: OncePerTurnWeaponHitDamageRider,
    attack: WeaponAttack,
) -> BonusDamageSpec:
    return (
        rider.source_name,
        rider.dice_count,
        rider.dice_size,
        rider.flat_bonus,
        DamageType(rider.damage_type) if rider.damage_type is not None else attack.weapon.damage_type,
    )


def once_per_turn_weapon_hit_bonus_damages(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    target: CombatantState | None = None,
) -> list[BonusDamageSpec]:
    """Return every independently qualifying generic once-per-turn weapon-hit rider."""
    try:
        if turn_key is None:
            raise ValueError("Once-per-turn hit riders require the actual active-turn key.")
        features = attacker.template.progression_features
        riders = [
            *([features.once_per_turn_weapon_hit_damage_rider]
              if features.once_per_turn_weapon_hit_damage_rider is not None else []),
            *features.once_per_turn_weapon_hit_damage_riders,
        ]
        result: list[BonusDamageSpec] = []
        seen_ids: set[str] = set()
        for rider in riders:
            if rider.source_id in seen_ids:
                raise ValueError(f"Duplicate once-per-turn hit rider source id: {rider.source_id}.")
            seen_ids.add(rider.source_id)
            if attacker.feature_last_turn_keys.get(rider.source_id) == turn_key:
                continue
            if not _qualified(rider, target):
                continue
            attacker.feature_last_turn_keys[rider.source_id] = turn_key
            result.append(_spec(rider, attack))
        return result
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed once-per-turn hit rider resolution for %s.", attacker.template.name)
        raise RuntimeError("Once-per-turn weapon-hit damage riders could not be resolved.") from exc


def once_per_turn_weapon_hit_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    target: CombatantState | None = None,
) -> BonusDamageSpec | None:
    """Compatibility wrapper for callers expecting at most one rider."""
    values = once_per_turn_weapon_hit_bonus_damages(attacker, attack, turn_key, target)
    return values[0] if values else None
