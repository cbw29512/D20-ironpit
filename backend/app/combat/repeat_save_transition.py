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
    """End a repeat-save effect or escalate it while preserving any continuing save lifecycle."""
    try:
        if succeeded:
            return remove_effect_group(state, effect), []
        if effect.repeat_save_failure_condition is None:
            return [], []
        removed = remove_effect_group(state, effect)
        escalated = apply_timed_condition(
            state,
            effect.repeat_save_failure_condition,
            effect.source_id,
            source_effect_id=effect.source_effect_id,
            applied_round=round_number,
            repeat_save_ability=effect.repeat_save_ability,
            repeat_save_dc=effect.repeat_save_dc,
            repeat_save_timing=effect.repeat_save_timing,
            automatic_success_after_rounds=_remaining_auto_success_rounds(effect, round_number),
            allowed_removal_action_ids=list(effect.allowed_removal_action_ids),
            ends_on_damage=effect.ends_on_damage,
            ends_if_source_incapacitated=effect.ends_if_source_incapacitated,
            ends_if_source_dead=effect.ends_if_source_dead,
        )
        return removed, [escalated] if escalated is not None else []
    except Exception:
        logger.exception("Failed repeat-save transition for %s.", effect.source_effect_id or effect.effect_id)
        raise
