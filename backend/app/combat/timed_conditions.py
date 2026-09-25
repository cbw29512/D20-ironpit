from __future__ import annotations

import logging

from app.combat.concentration import end_concentration_if_incapacitated
from app.combat.condition_immunity import condition_is_immune
from app.combat.debuff_counters import movement_counter_cost
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.combatants import DamageType
from app.domain.models import CombatantState, CombatantTemplate, DebuffCounter, TimedEffect
from app.domain.runtime import TimedTurnBehavior
from app.combat.timed_condition_lifecycle import (
    expire_start_of_turn_conditions,
    remove_effect_group,
    remove_effect_instance,
)

logger = logging.getLogger(__name__)

POISONED_EFFECT_ID = "poisoned"
ARENA_POISON_RECOVERY_DC = 10


def apply_timed_condition(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    *,
    source_effect_id: str | None = None,
    source_template: CombatantTemplate | None = None,
    source_is_magical: bool = False,
    suppress_action: bool = False,
    suppress_bonus_action: bool = False,
    suppress_reactions: bool = False,
    suppress_movement: bool = False,
    zero_hp_replacement_hp: int = 0,
    applied_round: int | None = None,
    expires_round: int | None = None,
    expires_at_start_of_source_turn: bool = True,
    expiry_timing: ConditionTiming | None = None,
    repeat_save_ability: AbilityName | None = None,
    repeat_save_dc: int | None = None,
    repeat_save_timing: ConditionTiming | None = None,
    allowed_removal_action_ids: list[str] | None = None,
    affected_states: list[CombatantState] | None = None,
    turn_behavior: TimedTurnBehavior = "normal",
    ends_on_damage: bool = False,
    ends_if_source_incapacitated: bool = False,
    ends_if_source_dead: bool = False,
    owned_damage_resistances: list[DamageType] | None = None,
    owned_debuff_counters: list[DebuffCounter] | None = None,
    use_default_poison_recovery: bool = True,
) -> str | None:
    """Apply one source-owned timed condition and its optional passive defenses.

    Passive defenses live on the same TimedEffect as the condition so normal
    lifecycle cleanup removes only state owned by this source. Callers supply
    source-specific parameters; damage math and expiry remain universal.
    """
    try:
        if condition_is_immune(
            state,
            effect_id,
            source_template,
            source_is_magical=source_is_magical,
        ):
            return None
        if effect_id == POISONED_EFFECT_ID and use_default_poison_recovery:
            if any(effect.effect_id == POISONED_EFFECT_ID for effect in state.timed_effects):
                return POISONED_EFFECT_ID
            expires_at_start_of_source_turn = False
            expiry_timing = None
            repeat_save_ability = repeat_save_ability or "constitution"
            repeat_save_dc = repeat_save_dc or ARENA_POISON_RECOVERY_DC
            repeat_save_timing = "target_turn_start"
        state.timed_effects = [
            effect for effect in state.timed_effects
            if not (
                effect.effect_id == effect_id
                and effect.source_id == source_id
                and effect.source_effect_id == source_effect_id
            )
        ]
        state.timed_effects.append(TimedEffect(
            effect_id=effect_id,
            source_id=source_id,
            source_effect_id=source_effect_id,
            applied_round=applied_round,
            expires_round=expires_round,
            expires_at_start_of_source_turn=expires_at_start_of_source_turn,
            expiry_timing=expiry_timing,
            repeat_save_ability=repeat_save_ability,
            repeat_save_dc=repeat_save_dc,
            repeat_save_timing=repeat_save_timing,
            allowed_removal_action_ids=allowed_removal_action_ids or [],
            turn_behavior=turn_behavior,
            ends_on_damage=ends_on_damage,
            ends_if_source_incapacitated=ends_if_source_incapacitated,
            ends_if_source_dead=ends_if_source_dead,
            source_is_magical=source_is_magical,
            suppress_action=suppress_action,
            suppress_bonus_action=suppress_bonus_action,
            suppress_reactions=suppress_reactions,
            suppress_movement=suppress_movement,
            zero_hp_replacement_hp=zero_hp_replacement_hp,
            owned_damage_resistances=owned_damage_resistances or [],
            owned_debuff_counters=owned_debuff_counters or [],
        ))
        if effect_id not in state.active_effect_ids:
            state.active_effect_ids.append(effect_id)
        end_concentration_if_incapacitated(state, affected_states)
        return effect_id
    except Exception:
        logger.exception(
            "Failed to apply timed condition %s from source %s (%s)",
            effect_id,
            source_id,
            source_effect_id,
        )
        raise


def resolve_movement_countered_conditions(state: CombatantState) -> list[tuple[str, str, int]]:
    """Automatically spend movement to clear active debuffs when a buff grants that option."""
    resolved: list[tuple[str, str, int]] = []
    for effect in list(state.timed_effects):
        cost = movement_counter_cost(
            state,
            effect.effect_id,
            source_is_magical=effect.source_is_magical,
        )
        if cost is None or state.movement_remaining_ft < cost:
            continue
        removed = remove_effect_group(state, effect)
        if not removed:
            continue
        state.movement_remaining_ft -= cost
        for condition_id in removed:
            resolved.append((condition_id, effect.source_id, cost))
    return resolved

