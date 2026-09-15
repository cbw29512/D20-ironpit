from __future__ import annotations

import logging

from app.combat.death_trigger_support import compile_action, distance_ft
from app.combat.dice import DiceProvider
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def resolve_death_triggers(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    *,
    resolved: set[str] | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve immutable on-death save effects once, including deterministic chain deaths."""
    try:
        if not source.state.is_dead:
            return [], sequence
        resolved_keys = resolved if resolved is not None else set()
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        events: list[BattleEvent] = []
        members = [*setup.heroes, *setup.monsters]
        for effect in source.state.template.death_trigger_effects:
            key = f"{source.combatant_id}:{effect.id}"
            if key in resolved_keys:
                continue
            resolved_keys.add(key)
            action = compile_action(effect)
            targets = [
                target for target in members
                if target.combatant_id != source.combatant_id
                and not target.state.is_dead
                and distance_ft(source, target) <= effect.radius_ft
            ]
            shared_rolls: list[int] = []
            newly_dead: list[EncounterCombatant] = []
            for index, target in enumerate(targets):
                was_dead = target.state.is_dead
                event = resolve_save_action(
                    sequence,
                    round_number,
                    source,
                    target,
                    action,
                    distance_ft(source, target),
                    dice,
                    spend_action=False,
                    spend_resource_cost=False,
                    shared_damage_rolls=shared_rolls or None,
                    capture_shared_damage_rolls=shared_rolls if index == 0 else None,
                    affected_states=affected_states,
                    setup=setup,
                )
                events.append(event)
                sequence += 1
                if not was_dead and target.state.is_dead and target.state.template.death_trigger_effects:
                    newly_dead.append(target)
            for dead_target in newly_dead:
                chained, sequence = resolve_death_triggers(
                    sequence,
                    round_number,
                    dead_target,
                    setup,
                    dice,
                    resolved=resolved_keys,
                )
                events.extend(chained)
        return events, sequence
    except Exception as exc:
        logger.exception("Death-trigger resolution failed for %s.", source.combatant_id)
        raise RuntimeError("Death-trigger resolution could not be completed.") from exc


def resolve_event_death_triggers(
    sequence: int,
    round_number: int,
    event: BattleEvent,
    setup: EncounterSetup,
    dice: DiceProvider,
    *,
    resolved: set[str] | None = None,
) -> tuple[list[BattleEvent], int]:
    """Dispatch on-death effects only for an event that itself records a lethal transition."""
    try:
        if not event.target_id or event.is_dead is not True:
            return [], sequence
        target = next(
            (member for member in [*setup.heroes, *setup.monsters] if member.combatant_id == event.target_id),
            None,
        )
        if target is None or not target.state.is_dead or not target.state.template.death_trigger_effects:
            return [], sequence
        return resolve_death_triggers(sequence, round_number, target, setup, dice, resolved=resolved)
    except Exception:
        logger.exception("Failed to dispatch death triggers after event %s.", event.sequence)
        raise
