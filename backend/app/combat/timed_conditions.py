from __future__ import annotations

import logging

from app.combat.concentration import end_concentration_if_incapacitated
from app.combat.condition_immunity import condition_is_immune
from app.combat.debuff_counters import movement_counter_cost
from app.combat.instant_death import apply_terminal_death
from app.combat.replacement_form_lifecycle import revert_replacement_form_if_incapacitated
from app.domain.actions import AbilityName, ConditionTiming
from app.domain.combatants import DamageType
from app.domain.models import CombatantState, CombatantTemplate, DebuffCounter, TimedEffect
from app.domain.movement import MovementModeGrant
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.runtime import TimedTurnBehavior
from app.combat.timed_condition_lifecycle import (
    expire_start_of_turn_conditions,
    remove_effect_group,
    remove_effect_instance,
)

logger = logging.getLogger(__name__)

POISONED_EFFECT_ID = "poisoned"
ARENA_POISON_RECOVERY_DC = 10
TERMINAL_CONDITIONS = frozenset({"petrified"})


def apply_terminal_condition_outcome(
    state: CombatantState,
    effect_id: str,
    *,
    affected_states: list[CombatantState] | None = None,
) -> bool:
    """Apply Iron Pit terminal consequences for semantic condition states."""
    if effect_id not in TERMINAL_CONDITIONS or state.is_dead:
        return False
    return apply_terminal_death(state, affected_states=affected_states) == "dead"


def apply_timed_condition(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    *,
    source_effect_id: str | None = None,
    source_template: CombatantTemplate | None = None,
    source_is_magical: bool = False,
    repeat_save_context: SavingThrowContext | None = None,
    suppress_action: bool = False,
    suppress_bonus_action: bool = False,
    suppress_reactions: bool = False,
    suppress_movement: bool = False,
    next_attack_disadvantage: bool = False,
    zero_hp_replacement_hp: int = 0,
    applied_round: int | None = None,
    expires_round: int | None = None,
    expires_target_turn_count: int | None = None,
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
    owned_movement_mode_grants: list[MovementModeGrant] | None = None,
    removed_from_battlefield: bool = False,
    return_damage_dice_count: int = 0,
    return_damage_dice_size: int = 0,
    return_damage_bonus: int = 0,
    return_damage_type: DamageType | None = None,
    return_damage_excluded_creature_types: list[str] | None = None,
    use_default_poison_recovery: bool = True,
    repeat_save_failures_to_lock: int | None = None,
    repeat_save_failure_condition_id: str | None = None,
    escape_check_ability: AbilityName | None = None,
    escape_check_dc: int | None = None,
    ground_contact: bool = False,
    active_ally_present: bool = False,
    ends_on_teleport: bool = False,
    source_effect_immunity_on_end: bool = False,
    control_limits=None,
) -> str | None:
    """Apply defenses and repeat-save context through one source-owned lifecycle."""
    try:
        if condition_is_immune(
            state,
            effect_id,
            source_template,
            source_is_magical=source_is_magical,
            ground_contact=ground_contact,
            active_ally_present=active_ally_present,
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
            expires_target_turn_count=expires_target_turn_count,
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
            repeat_save_context=repeat_save_context,
            suppress_action=suppress_action,
            suppress_bonus_action=suppress_bonus_action,
            suppress_reactions=suppress_reactions,
            suppress_movement=suppress_movement,
            next_attack_disadvantage=next_attack_disadvantage,
            zero_hp_replacement_hp=zero_hp_replacement_hp,
            owned_damage_resistances=owned_damage_resistances or [],
            owned_debuff_counters=owned_debuff_counters or [],
            owned_movement_mode_grants=owned_movement_mode_grants or [],
            removed_from_battlefield=removed_from_battlefield,
            return_damage_dice_count=return_damage_dice_count,
            return_damage_dice_size=return_damage_dice_size,
            return_damage_bonus=return_damage_bonus,
            return_damage_type=return_damage_type,
            return_damage_excluded_creature_types=return_damage_excluded_creature_types or [],
            repeat_save_failures_to_lock=repeat_save_failures_to_lock,
            repeat_save_failure_condition_id=repeat_save_failure_condition_id,
            escape_check_ability=escape_check_ability,
            escape_check_dc=escape_check_dc,
            ground_contact=ground_contact,
            ends_on_teleport=ends_on_teleport or ground_contact,
            source_effect_immunity_on_end=source_effect_immunity_on_end,
            control_limits=control_limits,
        ))
        if effect_id not in state.active_effect_ids:
            state.active_effect_ids.append(effect_id)
        if (
            effect_id == "unconscious"
            and "prone" not in state.active_effect_ids
            and not condition_is_immune(state, "prone")
        ):
            state.active_effect_ids.append("prone")
        apply_terminal_condition_outcome(state, effect_id, affected_states=affected_states)
        revert_replacement_form_if_incapacitated(state)
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
    from app.combat.flight_ground_immunity import resolve_flight_countered_ground_conditions

    resolved: list[tuple[str, str, int]] = list(resolve_flight_countered_ground_conditions(state))
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

