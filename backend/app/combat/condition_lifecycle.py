from __future__ import annotations

import logging

from app.combat.condition_lifecycle_support import (
    condition_name,
    expiry_due,
    grant_end_immunity,
    repeat_save_due,
)
from app.combat.modifier_stack import expire_target_turn_modifiers
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.domain.actions import ConditionTiming
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _escalate_repeat_failure(target, effect, round_number: int) -> tuple[list[str], list[str]]:
    condition_id = effect.repeat_save_failure_condition_id
    if condition_id is None:
        return [], []
    removed = remove_effect_group(target.state, effect)
    applied = apply_timed_condition(
        target.state, condition_id, effect.source_id,
        source_effect_id=effect.source_effect_id, applied_round=round_number,
        expires_at_start_of_source_turn=False,
    )
    return removed, [applied] if applied else []


def resolve_target_condition_timing(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    timing: ConditionTiming,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve expiry and one repeat save per grouped source effect on the affected creature's turn."""
    try:
        events: list[BattleEvent] = []
        for effect in list(target.state.timed_effects):
            if effect not in target.state.timed_effects:
                continue
            if timing == "target_turn_start" and effect.expires_after_next_target_turn:
                effect.target_turn_started_since_applied = True
            if repeat_save_due(effect, round_number, timing):
                roll, succeeded = resolve_saving_throw(
                    target.state, effect.repeat_save_ability, effect.repeat_save_dc, dice,
                    against_condition=effect.effect_id,
                )
                removed = remove_effect_group(target.state, effect) if succeeded else []
                escalated_removed, escalated_applied = ([], []) if succeeded else _escalate_repeat_failure(target, effect, round_number)
                if succeeded:
                    grant_end_immunity(target, effect)
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="saving_throw",
                    actor_id=target.combatant_id, actor_name=target.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    saving_throw_roll=roll, save_ability=effect.repeat_save_ability,
                    save_dc=effect.repeat_save_dc, save_succeeded=succeeded,
                    removed_condition_ids=[*removed, *escalated_removed], applied_condition_ids=escalated_applied,
                    feature_id=effect.source_effect_id or "condition-repeat-save", animation="condition-save",
                    description=(
                        f"{target.state.template.name} repeats the {effect.repeat_save_ability.title()} save "
                        f"against {condition_name(effect.source_effect_id or effect.effect_id)}: "
                        f"{'SUCCESS' if succeeded else 'FAILURE'}."
                    ),
                ))
                sequence += 1
                if succeeded or escalated_applied:
                    continue
            if expiry_due(effect, round_number, timing):
                removed = remove_effect_group(target.state, effect)
                if removed:
                    grant_end_immunity(target, effect)
                    events.append(BattleEvent(
                        sequence=sequence, round_number=round_number, event_type="feature",
                        actor_id=target.combatant_id, actor_name=target.state.template.name,
                        target_id=target.combatant_id, target_name=target.state.template.name,
                        removed_condition_ids=removed, feature_id=effect.source_effect_id or "condition-ended",
                        animation="condition-ended",
                        description=f"{condition_name(effect.source_effect_id or effect.effect_id)} ends on {target.state.template.name}.",
                    ))
                    sequence += 1
        if timing == "target_turn_end":
            expire_target_turn_modifiers(target.state)
        return events, sequence
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Target condition lifecycle failed for %s at %s.", target.combatant_id, timing)
        raise RuntimeError("Target condition lifecycle could not be resolved.") from exc


def resolve_source_condition_timing(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    timing: ConditionTiming,
) -> tuple[list[BattleEvent], int]:
    """Expire grouped conditions whose source-relative duration ends at this timing."""
    try:
        events: list[BattleEvent] = []
        for target in [*setup.heroes, *setup.monsters]:
            expiring = [effect for effect in target.state.timed_effects if effect.source_id == source.combatant_id and expiry_due(effect, round_number, timing)]
            for effect in expiring:
                if effect not in target.state.timed_effects:
                    continue
                removed = remove_effect_group(target.state, effect)
                if not removed:
                    continue
                grant_end_immunity(target, effect)
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number, event_type="feature",
                    actor_id=source.combatant_id, actor_name=source.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    removed_condition_ids=removed, feature_id=effect.source_effect_id or "condition-ended",
                    animation="condition-ended",
                    description=f"{condition_name(effect.source_effect_id or effect.effect_id)} ends on {target.state.template.name}.",
                ))
                sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Source condition lifecycle failed for %s.", source.combatant_id)
        raise RuntimeError("Source condition lifecycle could not be resolved.") from exc
