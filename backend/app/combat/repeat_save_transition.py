from __future__ import annotations

import logging

from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.domain.models import CombatantState, TimedEffect

logger = logging.getLogger(__name__)


def _remaining_auto_success_rounds(effect: TimedEffect, round_number: int) -> int | None:
    try:
        if effect.automatic_success_round is None:
            return None
        return max(1, effect.automatic_success_round - round_number)
    except Exception:
        logger.exception("Failed to preserve staged repeat-save duration for %s.", effect.source_effect_id or effect.effect_id)
        raise


def resolve_repeat_save_transition(
    state: CombatantState, effect: TimedEffect, succeeded: bool, round_number: int,
) -> tuple[list[str], list[str]]:
    """End a repeat-save effect or escalate it using the source-defined second-stage lifecycle."""
    try:
        if succeeded:
            return remove_effect_group(state, effect), []
        if effect.repeat_save_failure_condition is None:
            return [], []
        removed = remove_effect_group(state, effect)
        continues = effect.repeat_save_failure_continues
        duration = effect.repeat_save_failure_duration_rounds
        escalated = apply_timed_condition(
            state,
            effect.repeat_save_failure_condition,
            effect.source_id,
            source_effect_id=effect.source_effect_id,
            applied_round=round_number,
            expires_round=round_number + duration if duration is not None else None,
            expiry_timing="target_turn_end" if duration is not None else None,
            repeat_save_ability=effect.repeat_save_ability if continues else None,
            repeat_save_dc=effect.repeat_save_dc if continues else None,
            repeat_save_timing=effect.repeat_save_timing if continues else None,
            automatic_success_after_rounds=(
                _remaining_auto_success_rounds(effect, round_number) if continues else None
            ),
            allowed_removal_action_ids=(
                list(effect.repeat_save_failure_allowed_removal_action_ids)
                if effect.repeat_save_failure_allowed_removal_action_ids
                else list(effect.allowed_removal_action_ids)
            ),
            ends_on_damage=effect.repeat_save_failure_ends_on_damage or effect.ends_on_damage,
            ends_if_source_incapacitated=effect.ends_if_source_incapacitated,
            ends_if_source_dead=effect.ends_if_source_dead,
        )
        return removed, [escalated] if escalated is not None else []
    except Exception:
        logger.exception("Failed repeat-save transition for %s.", effect.source_effect_id or effect.effect_id)
        raise
