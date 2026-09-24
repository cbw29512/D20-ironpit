from __future__ import annotations

import logging

from app.domain.models import CombatantState, DamageType, WeaponAttack

logger = logging.getLogger(__name__)
BonusDamageSpec = tuple[str, int, int, DamageType]


def once_per_turn_weapon_hit_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
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
        if attacker.feature_last_turn_keys.get(rider.source_id) == turn_key:
            return None
        attacker.feature_last_turn_keys[rider.source_id] = turn_key
        return (
            rider.source_name,
            rider.dice_count,
            rider.dice_size,
            DamageType(rider.damage_type),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed once-per-turn hit rider resolution for %s.", attacker.template.name)
        raise RuntimeError("Once-per-turn weapon-hit damage rider could not be resolved.") from exc
