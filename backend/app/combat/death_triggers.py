from __future__ import annotations

from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction


def _combatants(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _pending_source(setup: EncounterSetup) -> EncounterCombatant | None:
    return next((member for member in _combatants(setup) if member.state.pending_death_trigger_ids), None)


def _action(source: EncounterCombatant, action_id: str) -> SavingThrowAction:
    action = next(
        (item for item in source.state.template.death_trigger_save_actions if item.id == action_id),
        None,
    )
    if action is None:
        raise ValueError(
            f"Pending death trigger {action_id!r} is missing from {source.state.template.name}."
        )
    return action


def _targets(source: EncounterCombatant, setup: EncounterSetup, action: SavingThrowAction):
    return [
        member for member in _combatants(setup)
        if member.combatant_id != source.combatant_id
        and member.state.is_alive and not member.state.is_dead
        and combatant_distance(source, member) <= action.range_ft
    ]


def resolve_pending_death_triggers(
    sequence: int,
    round_number: int,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve queued death effects immediately, including chain-triggered deaths."""
    events: list[BattleEvent] = []
    affected_states = [member.state for member in _combatants(setup)]
    while (source := _pending_source(setup)) is not None:
        action_id = source.state.pending_death_trigger_ids.pop(0)
        action = _action(source, action_id)
        targets = _targets(source, setup, action)
        shared_damage_rolls: list[int] | None = None
        for target in targets:
            event = resolve_save_action(
                sequence,
                round_number,
                source,
                target,
                action,
                combatant_distance(source, target),
                dice,
                spend_action=False,
                spend_resource_cost=False,
                shared_damage_rolls=shared_damage_rolls,
                affected_states=affected_states,
            )
            events.append(event)
            sequence += 1
            if shared_damage_rolls is None and event.damage_components:
                shared_damage_rolls = list(event.damage_components[0].rolls)
    return events, sequence
