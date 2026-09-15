from __future__ import annotations

from app.domain.models import CombatantState, TimedEffect


def apply_roll_penalty(
    state: CombatantState,
    *,
    effect_id: str,
    attack_roll_disadvantage: bool,
    ability_check_disadvantage: bool,
    expires_after_next_target_turn: bool,
) -> str:
    """Apply or refresh one declarative temporary roll penalty."""
    state.timed_effects = [
        effect for effect in state.timed_effects
        if not (effect.effect_id == effect_id and effect.source_effect_id == effect_id)
    ]
    state.timed_effects.append(TimedEffect(
        effect_id=effect_id,
        source_id=effect_id,
        source_effect_id=effect_id,
        expires_at_start_of_source_turn=False,
        disadvantage_attack_rolls=attack_roll_disadvantage,
        disadvantage_ability_checks=ability_check_disadvantage,
        expires_after_next_target_turn=expires_after_next_target_turn,
    ))
    if effect_id not in state.active_effect_ids:
        state.active_effect_ids.append(effect_id)
    return effect_id


def attack_roll_disadvantage(state: CombatantState) -> int:
    return int(any(effect.disadvantage_attack_rolls for effect in state.timed_effects))


def ability_check_disadvantage(state: CombatantState) -> int:
    return int(any(effect.disadvantage_ability_checks for effect in state.timed_effects))
