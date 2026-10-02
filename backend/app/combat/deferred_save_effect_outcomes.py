from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage, reduce_to_zero_hit_points
from app.domain.models import CombatantState, DamageRollComponent, DamageType, DiceRoll
from app.domain.progression import DeferredSaveEffect

logger = logging.getLogger(__name__)


def _apply_typed_damage(
    target: CombatantState,
    rule: DeferredSaveEffect,
    *,
    dice_count: int,
    dice_size: int,
    damage_type_name: str,
    multiplier: float,
    dice,
    affected_states: list[CombatantState],
) -> tuple[DiceRoll, list[DamageRollComponent]]:
    """Roll one deferred damage packet, apply save scaling, then shared defenses."""
    try:
        rolls = [dice.roll(dice_size) for _ in range(dice_count)]
        rolled_total = sum(rolls)
        scaled_total = int(rolled_total * multiplier)
        damage_type = DamageType(damage_type_name)
        raw = DamageRollComponent(
            source=rule.source_name,
            notation=f"{dice_count}d{dice_size}",
            rolls=rolls,
            modifier=0,
            damage_type=damage_type,
            total=scaled_total,
        )
        applied, components = apply_damage_defenses(target, [raw])
        apply_damage(
            target,
            applied,
            damage_types={damage_type},
            dice=dice,
            affected_states=affected_states,
        )
        return (
            DiceRoll(
                notation=raw.notation,
                rolls=rolls,
                modifier=0,
                total=applied,
            ),
            components,
        )
    except Exception as exc:
        logger.exception("Failed deferred typed damage for %s.", rule.source_name)
        raise RuntimeError("Deferred typed damage could not be resolved.") from exc


def resolve_deferred_effect_outcome(
    target: CombatantState,
    rule: DeferredSaveEffect,
    succeeded: bool,
    dice,
    affected_states: list[CombatantState],
) -> tuple[DiceRoll | None, list[DamageRollComponent]]:
    """Apply one configured deferred save outcome through shared damage/zero-HP rules."""
    try:
        if rule.failure_damage_dice_count:
            if rule.failure_damage_type is None:
                raise ValueError(
                    f"Deferred effect {rule.source_id} has failure damage dice without a damage type."
                )
            multiplier = 0.5 if succeeded and rule.success_damage_from_failure == "half" else 1.0
            if succeeded and rule.success_damage_from_failure == "none":
                return None, []
            return _apply_typed_damage(
                target,
                rule,
                dice_count=rule.failure_damage_dice_count,
                dice_size=rule.failure_damage_dice_size,
                damage_type_name=rule.failure_damage_type,
                multiplier=multiplier,
                dice=dice,
                affected_states=affected_states,
            )

        if succeeded and rule.success_damage_dice_count:
            if rule.success_damage_type is None:
                raise ValueError(
                    f"Deferred effect {rule.source_id} has damage dice without a damage type."
                )
            return _apply_typed_damage(
                target,
                rule,
                dice_count=rule.success_damage_dice_count,
                dice_size=rule.success_damage_dice_size,
                damage_type_name=rule.success_damage_type,
                multiplier=1.0,
                dice=dice,
                affected_states=affected_states,
            )

        if not succeeded and rule.failure_sets_zero_hp:
            reduce_to_zero_hit_points(
                target,
                dice=dice,
                affected_states=affected_states,
            )
        return None, []
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed deferred save outcome for %s.", rule.source_name)
        raise RuntimeError("Deferred save outcome could not be resolved.") from exc
