from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_removal import remove_condition
from app.combat.modifier_stack import expire_target_turn_modifiers
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_terminal_condition_outcome, remove_effect_group
from app.domain.actions import ConditionTiming
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _condition_name(effect_id: str) -> str:
    return effect_id.replace("_", " ").title()


def _repeat_save_due(effect, round_number: int, timing: ConditionTiming) -> bool:
    if effect.repeat_save_timing != timing:
        return False
    return not (
        effect.effect_id == "poisoned"
        and effect.applied_round is not None
        and round_number <= effect.applied_round
    )


def _expiry_due(effect, round_number: int, timing: ConditionTiming) -> bool:
    return effect.expiry_timing == timing and (
        effect.expires_round is None or round_number >= effect.expires_round
    )


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
            if _repeat_save_due(effect, round_number, timing):
                roll, succeeded = resolve_saving_throw(
                    target.state,
                    effect.repeat_save_ability,
                    effect.repeat_save_dc,
                    dice,
                )
                removed = remove_effect_group(target.state, effect) if succeeded else []
                applied: list[str] = []
                if not succeeded:
                    effect.repeat_save_failure_count += 1
                    if effect.repeat_save_failure_condition_id is not None:
                        removed = remove_effect_group(target.state, effect)
                        escalated = effect.repeat_save_failure_condition_id
                        if not condition_is_immune(target.state, escalated):
                            if escalated not in target.state.active_effect_ids:
                                target.state.active_effect_ids.append(escalated)
                            apply_terminal_condition_outcome(target.state, escalated)
                            applied.append(escalated)
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="saving_throw",
                    actor_id=target.combatant_id,
                    actor_name=target.state.template.name,
                    target_id=target.combatant_id,
                    target_name=target.state.template.name,
                    saving_throw_roll=roll,
                    save_ability=effect.repeat_save_ability,
                    save_dc=effect.repeat_save_dc,
                    save_succeeded=succeeded,
                    applied_condition_ids=applied,
                    removed_condition_ids=removed,
                    feature_id=effect.source_effect_id or "condition-repeat-save",
                    animation="condition-save",
                    description=(
                        f"{target.state.template.name} repeats the {effect.repeat_save_ability.title()} save "
                        f"against {_condition_name(effect.source_effect_id or effect.effect_id)}: "
                        f"{'SUCCESS' if succeeded else 'FAILURE'}."
                    ),
                ))
                sequence += 1
                if succeeded:
                    continue
            if _expiry_due(effect, round_number, timing):
                removed = remove_effect_group(target.state, effect)
                if removed:
                    events.append(BattleEvent(
                        sequence=sequence,
                        round_number=round_number,
                        event_type="feature",
                        actor_id=target.combatant_id,
                        actor_name=target.state.template.name,
                        target_id=target.combatant_id,
                        target_name=target.state.template.name,
                        removed_condition_ids=removed,
                        feature_id=effect.source_effect_id or "condition-ended",
                        animation="condition-ended",
                        description=f"{_condition_name(effect.source_effect_id or effect.effect_id)} ends on {target.state.template.name}.",
                    ))
                    sequence += 1
        if timing == "target_turn_end":
            grant = target.state.template.progression_features.end_turn_condition_removal
            if grant is not None:
                removed: list[str] = []
                for condition_id in grant.condition_ids:
                    if condition_id not in target.state.active_effect_ids:
                        continue
                    remove_condition(target, condition_id)
                    removed.append(condition_id)
                    if len(removed) >= grant.max_conditions:
                        break
                if removed:
                    events.append(BattleEvent(
                        sequence=sequence,
                        round_number=round_number,
                        event_type="feature",
                        actor_id=target.combatant_id,
                        actor_name=target.state.template.name,
                        target_id=target.combatant_id,
                        target_name=target.state.template.name,
                        removed_condition_ids=removed,
                        feature_id=grant.source_id,
                        animation="condition-ended",
                        description=(
                            f"{target.state.template.name} uses {grant.source_name}; "
                            f"{', '.join(item.replace('_', ' ').title() for item in removed)} ends."
                        ),
                    ))
                    sequence += 1
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
            expiring = [
                effect for effect in target.state.timed_effects
                if effect.source_id == source.combatant_id and _expiry_due(effect, round_number, timing)
            ]
            for effect in expiring:
                if effect not in target.state.timed_effects:
                    continue
                removed = remove_effect_group(target.state, effect)
                if not removed:
                    continue
                events.append(BattleEvent(
                    sequence=sequence,
                    round_number=round_number,
                    event_type="feature",
                    actor_id=source.combatant_id,
                    actor_name=source.state.template.name,
                    target_id=target.combatant_id,
                    target_name=target.state.template.name,
                    removed_condition_ids=removed,
                    feature_id=effect.source_effect_id or "condition-ended",
                    animation="condition-ended",
                    description=f"{_condition_name(effect.source_effect_id or effect.effect_id)} ends on {target.state.template.name}.",
                ))
                sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Source condition lifecycle failed for %s.", source.combatant_id)
        raise RuntimeError("Source condition lifecycle could not be resolved.") from exc
