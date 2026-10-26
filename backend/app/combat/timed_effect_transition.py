from __future__ import annotations

import logging

from app.domain.delayed_effect_transition import DelayedTimedEffectTransition
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def requires_timed_effect(rule, duration: int | None) -> bool:
    return any((
        duration is not None, rule.repeat_save_timing is not None,
        rule.effect_id is not None, rule.cannot_regain_hit_points,
        bool(rule.allowed_removal_action_ids), rule.curse_id is not None,
        rule.removal_effect_tag is not None, rule.delayed_transition is not None,
    ))


def schedule_on_hit_transition(
    state: CombatantState,
    effect_id: str,
    source_id: str,
    source_effect_id: str,
    rule,
) -> None:
    """Attach immutable lifecycle parameters to the exact fight-local effect."""
    try:
        effect = next((item for item in reversed(state.timed_effects)
                       if item.effect_id == effect_id and item.source_id == source_id
                       and item.source_effect_id == source_effect_id), None)
        if effect is None:
            raise ValueError(f"Applied timed effect {effect_id!r} could not be found.")
        effect.removal_effect_tag = rule.removal_effect_tag
        effect.minimum_removal_spell_level = rule.minimum_removal_spell_level
        effect.removal_action_exceptions = list(rule.removal_action_exceptions)
        if rule.delayed_transition is not None:
            transition = rule.delayed_transition
            effect.activates_target_turn_count = state.turns_started + transition.target_turns
            effect.pending_transition = transition.model_copy(deep=True)
    except Exception:
        logger.exception("Failed to schedule delayed transition for %s.", effect_id)
        raise


def activate_due_transitions(
    sequence: int, round_number: int, target,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for effect in list(target.state.timed_effects):
        due = effect.activates_target_turn_count
        rule = effect.pending_transition
        if due is None or rule is None or target.state.turns_started < due:
            continue
        effect.cannot_regain_hit_points = rule.cannot_regain_hit_points
        effect.removal_effect_tag = rule.removal_effect_tag
        effect.minimum_removal_spell_level = rule.minimum_removal_spell_level
        effect.removal_action_exceptions = list(rule.removal_action_exceptions)
        effect.activates_target_turn_count = None
        effect.pending_transition = None
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=target.combatant_id, actor_name=target.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=effect.source_effect_id or effect.effect_id,
            animation="condition-applied",
            description=(f"{effect.effect_id.replace('_', ' ').title()} advances on "
                         f"{target.state.template.name}."),
        ))
        sequence += 1
    return events, sequence
