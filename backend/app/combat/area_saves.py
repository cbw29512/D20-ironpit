from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.area_targeting import area_target_ids
from app.combat.resources import spend_action_resource
from app.combat.saving_throws import resolve_save_action, save_action_resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction


def resolve_area_save_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve one printed area action: one cost, one damage roll, independent saves."""
    if action.area is None:
        raise ValueError(f"{action.name} is not an area saving-throw action.")
    if not is_available(actor.state, "action"):
        raise ValueError("Action is not available for an area saving-throw action.")
    if not save_action_resource_available(actor.state, action):
        raise ValueError(f"{action.name} resource is unavailable.")
    target_ids = area_target_ids(actor, setup, action)
    if not target_ids:
        raise ValueError(f"{action.name} has no legal area targets.")

    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    affected_states = [member.state for member in members]
    spend(actor.state, "action")

    events: list[BattleEvent] = []
    shared_damage_rolls: list[int] | None = None
    for target_id in target_ids:
        target = by_id[target_id]
        event = resolve_save_action(
            sequence,
            round_number,
            actor,
            target,
            action,
            abs(actor.position_ft - target.position_ft),
            dice,
            spend_action=False,
            spend_resource=False,
            shared_damage_rolls=shared_damage_rolls,
            affected_states=affected_states,
        )
        events.append(event)
        if shared_damage_rolls is None and event.damage_components:
            shared_damage_rolls = list(event.damage_components[0].rolls)
        sequence += 1

    spend_action_resource(
        actor.state,
        action.resource_id,
        action.resource_cost,
        action_id=action.id,
    )
    if action.resource_id is not None:
        remaining = next(item.current_uses for item in actor.state.resources if item.id == action.resource_id)
        for event in events:
            event.resource_remaining = remaining
    return events, sequence
