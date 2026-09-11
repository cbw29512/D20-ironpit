from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.grapple import apply_grapple
from app.combat.hit_modifiers import apply_modifier_effect
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_penalties import apply_timed_penalty
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.runtime import CombatantState, TimedEffect
from app.domain.save_effects import (
    ConditionEffectDefinition,
    GrappleEffectDefinition,
    ProneEffectDefinition,
    SaveFailureEffectDefinition,
    TimedPenaltyEffectDefinition,
    TurnRestrictionEffectDefinition,
)
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)
PRONE_EFFECT_ID = "prone"
TURN_RESTRICTION_EFFECT_ID = "turn-restriction"


def _size_allowed(state: CombatantState, maximum) -> bool:
    return maximum is None or size_at_most(state.template.size, maximum)


def _apply_turn_restriction(
    target: CombatantState, source_id: str, source_effect_id: str,
    effect: TurnRestrictionEffectDefinition, round_number: int,
) -> str | None:
    required = effect.requires_condition
    if required is not None and required not in target.active_effect_ids:
        return None
    target.timed_effects = [item for item in target.timed_effects if not (
        item.effect_id == TURN_RESTRICTION_EFFECT_ID
        and item.source_id == source_id and item.source_effect_id == source_effect_id
    )]
    target.timed_effects.append(TimedEffect(
        effect_id=TURN_RESTRICTION_EFFECT_ID, source_id=source_id, source_effect_id=source_effect_id,
        applied_round=round_number, expiry_timing=effect.expiry_timing,
        action_or_bonus_only=effect.action_or_bonus_only, reactions_disabled=effect.reactions_disabled,
        speed_multiplier=effect.speed_multiplier, requires_active_effect_id=required,
    ))
    return TURN_RESTRICTION_EFFECT_ID


def _apply_condition(
    target: CombatantState, source_id: str, source_effect_id: str,
    effect: ConditionEffectDefinition, round_number: int,
    affected_states: list[CombatantState] | None,
) -> list[str]:
    condition = apply_timed_condition(
        target, effect.condition, source_id, source_effect_id=source_effect_id,
        applied_round=round_number, expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
        expiry_timing=effect.expiry_timing, repeat_save_ability=effect.repeat_save_ability,
        repeat_save_dc=effect.repeat_save_dc, repeat_save_timing=effect.repeat_save_timing,
        repeat_save_delay_rounds=effect.repeat_save_delay_rounds,
        repeat_save_failure_condition=effect.repeat_save_failure_condition,
        allowed_removal_action_ids=effect.allowed_removal_action_ids,
        periodic_damage=effect.periodic_damage, affected_states=affected_states,
    )
    if condition is None:
        return []
    applied = [condition]
    for linked in effect.linked_conditions:
        linked_id = apply_timed_condition(
            target, linked, source_id, source_effect_id=source_effect_id,
            applied_round=round_number, affected_states=affected_states,
        )
        if linked_id is not None:
            applied.append(linked_id)
    return applied


def apply_save_failure_effects(
    target: CombatantState, source_id: str, source_effect_id: str,
    effects: list[SaveFailureEffectDefinition], *, round_number: int, range_ft: int,
    affected_states: list[CombatantState] | None = None,
) -> list[str]:
    """Apply failed-save effects in source order and return applied effect ids."""
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
                    applied.extend(apply_grapple(target, source_id, effect.escape_dc, range_ft, restrains=effect.restrains))
            elif isinstance(effect, ConditionEffectDefinition):
                if _size_allowed(target, effect.max_target_size):
                    applied.extend(_apply_condition(target, source_id, source_effect_id, effect, round_number, affected_states))
            elif isinstance(effect, TurnRestrictionEffectDefinition):
                restriction = _apply_turn_restriction(target, source_id, source_effect_id, effect, round_number)
                if restriction is not None:
                    applied.append(restriction)
            elif isinstance(effect, TimedPenaltyEffectDefinition):
                applied.append(apply_timed_penalty(
                    target, source_id, source_effect_id, round_number=round_number,
                    effect_family=effect.effect_family,
                    d20_disadvantage_ability=effect.d20_disadvantage_ability,
                    damage_penalty_dice_count=effect.damage_penalty_dice_count,
                    damage_penalty_dice_size=effect.damage_penalty_dice_size,
                    repeat_save_ability=effect.repeat_save_ability,
                    repeat_save_dc=effect.repeat_save_dc, repeat_save_timing=effect.repeat_save_timing,
                    automatic_success_after_rounds=effect.automatic_success_after_rounds,
                ))
            elif isinstance(effect, CombatModifierEffect):
                apply_modifier_effect(target, source_id, source_effect_id, effect, index, trigger="failed-save")
            else:
                raise ValueError(f"Unsupported failed-save effect: {effect!r}")
        return list(dict.fromkeys(applied))
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed-save effect resolution failed for %s.", source_effect_id)
        raise RuntimeError("Failed-save effects could not be resolved.") from exc
