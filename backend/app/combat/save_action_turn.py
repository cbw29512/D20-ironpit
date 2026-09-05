from __future__ import annotations

from app.combat.pit_policy import save_distance, target_order
from app.combat.save_action_resources import resource_available
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction


SaveChoice = tuple[SavingThrowAction, list[tuple[EncounterCombatant, int]]]


def choose_save_action(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    *,
    priority_only: bool = False,
) -> SaveChoice | None:
    actions = sorted(
        (
            action for action in attacker.state.template.saving_throw_actions
            if resource_available(attacker.state, action) and (not priority_only or action.priority > 0)
        ),
        key=lambda action: (-action.priority, action.id),
    )
    for action in actions:
        targets: list[tuple[EncounterCombatant, int]] = []
        for target in target_order(attacker, setup):
            distance = save_distance(attacker, target, action.range_ft)
            if legal_save_action(action, target, distance):
                targets.append((target, distance))
            if len(targets) >= action.area_slots:
                break
        if targets:
            return action, targets
    return None


def resolve_save_choice(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    choice: SaveChoice,
    dice,
) -> tuple[list[BattleEvent], int]:
    action, targets = choice
    affected = [member.state for member in [*setup.heroes, *setup.monsters]]
    events: list[BattleEvent] = []
    shared_damage_rolls: list[int] | None = None
    for index, (target, distance) in enumerate(targets):
        event = resolve_save_action(
            sequence, round_number, attacker, target, action, distance, dice,
            spend_action=index == 0, spend_resource=index == 0,
            shared_damage_rolls=shared_damage_rolls, affected_states=affected,
        )
        events.append(event)
        if shared_damage_rolls is None and event.damage_components:
            shared_damage_rolls = list(event.damage_components[0].rolls)
        sequence += 1
    return events, sequence
