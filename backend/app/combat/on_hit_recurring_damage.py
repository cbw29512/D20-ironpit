"""Add a universal nonstacking recurring damage debuff on a successful hit."""
from __future__ import annotations

import logging

from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def apply_recurring_damage_effect(target, spec, *, source_id: str,
                                  source_effect_id: str, source_name: str) -> str | None:
    """Attach an immutable source-owned recurring effect to fight-local state."""
    try:
        if spec is None or target.is_dead or not target.is_alive:
            return None
        if spec.tick_timing not in {"target_turn_start", "target_turn_end"} or spec.stacking != "nonstacking":
            raise ValueError("Unsupported recurring-hit damage policy.")
        if any(e.effect_id == spec.effect_id for e in target.timed_effects):
            return None
        target.timed_effects.append(TimedEffect(
            effect_id=spec.effect_id, source_id=source_id,
            source_effect_id=source_effect_id, source_name=source_name,
            ends_if_source_dead=spec.ends_if_source_dead,
            allowed_removal_action_ids=list(spec.removal_action_ids),
            expires_at_start_of_source_turn=False,
            end_of_turn_dice_count=spec.dice_count if spec.tick_timing == "target_turn_end" else 0,
            end_of_turn_dice_size=spec.dice_size,
            end_of_turn_damage_type=spec.damage_type if spec.tick_timing == "target_turn_end" else None,
            start_of_turn_dice_count=spec.dice_count if spec.tick_timing == "target_turn_start" else 0,
            start_of_turn_dice_size=spec.dice_size,
            start_of_turn_damage_type=spec.damage_type if spec.tick_timing == "target_turn_start" else None,
        ))
        if spec.effect_id not in target.active_effect_ids:
            target.active_effect_ids.append(spec.effect_id)
        return spec.effect_id
    except Exception:
        logger.exception("Failed to apply recurring damage from %s.", source_effect_id)
        raise


def apply_on_hit_recurring_damage(target, attack, *, source_id: str) -> str | None:
    """Existing weapon-hit trigger reuses the generic recurring-effect lifecycle."""
    try:
        spec = attack.on_hit_recurring_damage
        if spec is None:
            return None
        return apply_recurring_damage_effect(
            target, spec, source_id=source_id,
            source_effect_id=attack.id, source_name=attack.weapon.name,
        )
    except Exception:
        logger.exception("Failed on-hit recurring damage from %s.", attack.id)
        raise
