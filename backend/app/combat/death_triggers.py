from __future__ import annotations

from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _marker(action: SavingThrowAction) -> str:
    return f"death-trigger:{action.id}"


def _pending(setup: EncounterSetup) -> list[tuple[EncounterCombatant, SavingThrowAction]]:
    pending: list[tuple[EncounterCombatant, SavingThrowAction]] = []
    for source in _members(setup):
        if not source.state.is_dead:
            continue
        for action in source.state.template.death_trigger_actions:
            if _marker(action) not in source.state.feature_last_turn_keys:
                pending.append((source, action))
    return pending


def _targets(source: EncounterCombatant, action: SavingThrowAction, setup: EncounterSetup) -> list[EncounterCombatant]:
    return [
        target for target in _members(setup)
        if target.combatant_id != source.combatant_id
        and target.state.is_alive and not target.state.is_dead
        and combatant_distance(source, target) <= action.range_ft
    ]


def resolve_pending_death_triggers(
    sequence: int, round_number: int, setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve every newly-dead source once, including deterministic chain reactions."""
    events: list[BattleEvent] = []
    affected_states = [member.state for member in _members(setup)]
    while True:
        pending = _pending(setup)
        if not pending:
            return events, sequence
        for source, action in pending:
            source.state.feature_last_turn_keys[_marker(action)] = "fired"
            shared = [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)] if action.damage_dice_count else None
            for target in _targets(source, action, setup):
                event = resolve_save_action(
                    sequence, round_number, source, target, action, combatant_distance(source, target), dice,
                    spend_action=False, check_resource=False, spend_resource=False,
                    shared_damage_rolls=shared, affected_states=affected_states, setup=setup,
                )
                events.append(event); sequence += 1
