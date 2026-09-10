from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.grapple import apply_grapple
from app.combat.hit_modifiers import apply_modifier_effect
from app.combat.timed_conditions import apply_timed_condition
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.runtime import CombatantState
from app.domain.save_effects import (
    ConditionEffectDefinition,
    GrappleEffectDefinition,
    ProneEffectDefinition,
    SaveFailureEffectDefinition,
)
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)
PRONE_EFFECT_ID = "prone"


def _size_allowed(state: CombatantState, maximum) -> bool:
    return maximum is None or size_at_most(state.template.size, maximum)


def apply_save_failure_effects(
    target: CombatantState,
    source_id: str,
    source_effect_id: str,
    effects: list[SaveFailureEffectDefinition],
    *,
    round_number: int,
    range_ft: int,
    affected_states: list[CombatantState] | None = None,
) -> list[str]:
    """Apply failed-save effects in source order and return applied condition ids."""
    try:
        if target.is_dead or not target.is_alive:
            return []
        applied: list[str] = []
        for index, effect in enumerate(effects):
            if isinstance(effect, ProneEffectDefinition):
                if _size_allowed(target, effect.max_target_size) and not condition_is_immune(target, PRONE_EFFECT_ID):
                    if PRONE_EFFECT_ID not in target.active_effect_ids:
                        target.active_effect_ids.append(PRONE_EFFECT_ID)
                    applied.append(PRONE_EFFECT_ID)
            elif isinstance(effect, GrappleEffectDefinition):
                if _size_allowed(target, effect.max_target_size):
                    applied.extend(apply_grapple(
                        target, source_id, effect.escape_dc, range_ft, restrains=effect.restrains,
                    ))
            elif isinstance(effect, ConditionEffectDefinition):
                if not _size_allowed(target, effect.max_target_size):
                    continue
                condition = apply_timed_condition(
                    target,
                    effect.condition,
                    source_id,
                    source_effect_id=source_effect_id,
                    applied_round=round_number,
                    expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
                    expiry_timing=effect.expiry_timing,
                    repeat_save_ability=effect.repeat_save_ability,
                    repeat_save_dc=effect.repeat_save_dc,
                    repeat_save_timing=effect.repeat_save_timing,
                    repeat_save_delay_rounds=effect.repeat_save_delay_rounds,
                    allowed_removal_action_ids=effect.allowed_removal_action_ids,
                    affected_states=affected_states,
                )
                if condition is not None:
                    applied.append(condition)
            elif isinstance(effect, CombatModifierEffect):
                apply_modifier_effect(
                    target, source_id, source_effect_id, effect, index, trigger="failed-save",
                )
            else:
                raise ValueError(f"Unsupported failed-save effect: {effect!r}")
        return list(dict.fromkeys(applied))
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed-save effect resolution failed for %s.", source_effect_id)
        raise RuntimeError("Failed-save effects could not be resolved.") from exc
