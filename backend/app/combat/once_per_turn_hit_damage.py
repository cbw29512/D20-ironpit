from __future__ import annotations

import logging

from app.content.monster_creature_types import base_creature_type
from app.domain.models import CombatantState, DamageType, WeaponAttack

logger = logging.getLogger(__name__)
BonusDamageSpec = tuple[str, int, int, int, DamageType]


def once_per_turn_weapon_hit_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    target: CombatantState | None = None,
) -> BonusDamageSpec | None:
    """Return and consume a generic source-owned once-per-turn weapon-hit damage rider."""
    try:
        rider = attacker.template.progression_features.once_per_turn_weapon_hit_damage_rider
        if rider is None:
            return None
        if turn_key is None:
            raise ValueError(
                f"{rider.source_name} requires the actual active-turn key for once-per-turn tracking."
            )
        if rider.requires_target_below_max_hp:
            if target is None:
                raise ValueError(f"{rider.source_name} requires target state for its hit qualification.")
            if target.current_hp >= target.template.max_hp:
                return None
        if rider.target_creature_types:
            if target is None:
                raise ValueError(f"{rider.source_name} requires target state for its creature-type qualification.")
            target_type = base_creature_type(target.template.creature_type)
            if target_type not in rider.target_creature_types:
                return None
        if attacker.feature_last_turn_keys.get(rider.source_id) == turn_key:
            return None
        attacker.feature_last_turn_keys[rider.source_id] = turn_key
        return (
            rider.source_name,
            rider.dice_count,
            rider.dice_size,
            rider.flat_bonus,
            DamageType(rider.damage_type) if rider.damage_type is not None else attack.weapon.damage_type,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed once-per-turn hit rider resolution for %s.", attacker.template.name)
        raise RuntimeError("Once-per-turn weapon-hit damage rider could not be resolved.") from exc
