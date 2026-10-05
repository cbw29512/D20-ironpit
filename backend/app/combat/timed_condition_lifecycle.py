from __future__ import annotations

import logging

from app.domain.models import BattleEvent, CombatantState, EncounterCombatant, EncounterSetup, TimedEffect

logger = logging.getLogger(__name__)


def remove_effect_instance(state: CombatantState, effect: TimedEffect) -> bool:
    try:
        state.timed_effects = [item for item in state.timed_effects if item != effect]
        still_active = any(item.effect_id == effect.effect_id for item in state.timed_effects)
        if not still_active and effect.effect_id in state.active_effect_ids:
            state.active_effect_ids.remove(effect.effect_id)
            return True
        return not still_active
    except Exception:
        logger.exception("Failed to remove timed effect instance %s.", effect.effect_id)
        raise


def remove_effect_group(state: CombatantState, effect: TimedEffect) -> list[str]:
    try:
        if effect.source_effect_id is None:
            return [effect.effect_id] if remove_effect_instance(state, effect) else []
        grouped = [
            item for item in list(state.timed_effects)
            if item.source_id == effect.source_id
            and item.source_effect_id == effect.source_effect_id
        ]
        removed: list[str] = []
        for item in grouped:
            if remove_effect_instance(state, item):
                removed.append(item.effect_id)
        state.active_modifiers = [
            item for item in state.active_modifiers
            if not (
                item.source_id == effect.source_id
                and item.source_effect_id == effect.source_effect_id
            )
        ]
        return removed
    except Exception:
        logger.exception(
            "Failed to remove timed effect group %s from source %s.",
            effect.source_effect_id or effect.effect_id,
            effect.source_id,
        )
        raise


def _source_start_expired(effect: TimedEffect, round_number: int) -> bool:
    try:
        source_start = (
            effect.expiry_timing == "source_turn_start"
            or effect.expires_at_start_of_source_turn
        )
        return source_start and (
            effect.expires_round is None or round_number >= effect.expires_round
        )
    except Exception:
        logger.exception("Failed to evaluate timed effect expiry for %s.", effect.effect_id)
        raise


def expire_start_of_turn_conditions(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    try:
        events: list[BattleEvent] = []
        for target in [*setup.heroes, *setup.monsters]:
            expiring = [
                effect
                for effect in target.state.timed_effects
                if effect.source_id == source.combatant_id
                and _source_start_expired(effect, round_number)
            ]
            for effect in expiring:
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
                    description=(
                        f"{target.state.template.name} is no longer affected by "
                        f"{effect.source_effect_id or effect.effect_id}."
                    ),
                ))
                sequence += 1
        return events, sequence
    except Exception:
        logger.exception(
            "Failed start-of-turn timed effect expiry for %s in round %s.",
            source.combatant_id,
            round_number,
        )
        raise
