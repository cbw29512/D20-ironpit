from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.pit_policy import save_distance, target_order
from app.combat.saving_throws import legal_save_action, resolve_save_action, save_action_resource_available
from app.combat.spell_area import CARD_WIDTH_FT, MAX_CARD_SLOTS
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def _living(member: EncounterCombatant) -> bool:
    state = member.state
    return state.is_alive and not state.is_dead and state.current_hp > 0


def _side_rows(actor: EncounterCombatant, setup: EncounterSetup):
    if actor.side == "heroes":
        return setup.monsters, setup.heroes
    return setup.heroes, setup.monsters


def _forward_distance(actor: EncounterCombatant, member: EncounterCombatant) -> int:
    direction = 1 if actor.side == "heroes" else -1
    return (member.position_ft - actor.position_ft) * direction


def _slot_count(action: SavingThrowAction) -> int:
    area = action.area
    if area is None:
        return 1
    if area.shape not in {"cone", "line"}:
        raise ValueError(f"{action.name} area shape {area.shape!r} is not runtime-certified.")
    width = area.width_ft if area.shape == "line" else area.size_ft
    if width is None or width % CARD_WIDTH_FT:
        raise ValueError(f"{action.name} area width must use 5-foot card increments.")
    return min(MAX_CARD_SLOTS, max(1, width // CARD_WIDTH_FT))


def _area_targets(
    actor: EncounterCombatant, setup: EncounterSetup, action: SavingThrowAction,
) -> list[EncounterCombatant]:
    area = action.area
    if area is None:
        return []
    slot_count = _slot_count(action)
    enemies, friends = _side_rows(actor, setup)
    ordered_ids = {member.combatant_id: index for index, member in enumerate(target_order(actor, setup))}
    candidates: list[tuple[int, int, list[EncounterCombatant]]] = []
    for start in range(0, MAX_CARD_SLOTS - slot_count + 1):
        targets = [
            member for index, member in enumerate(enemies)
            if start <= index < start + slot_count and _living(member)
            and 0 < _forward_distance(actor, member) <= area.size_ft
            and legal_save_action(action, member, save_distance(actor, member, action.range_ft))
        ]
        if not targets:
            continue
        exposed_friend = any(
            member.combatant_id != actor.combatant_id and start <= index < start + slot_count
            and _living(member) and 0 < _forward_distance(actor, member) <= area.size_ft
            for index, member in enumerate(friends)
        )
        if exposed_friend:
            continue
        targets.sort(key=lambda member: ordered_ids.get(member.combatant_id, MAX_CARD_SLOTS))
        candidates.append((len(targets), -start, targets))
    if not candidates:
        return []
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _targets_for_action(
    actor: EncounterCombatant, setup: EncounterSetup, action: SavingThrowAction,
) -> list[EncounterCombatant]:
    if action.area is not None:
        return _area_targets(actor, setup, action)
    for target in target_order(actor, setup):
        if legal_save_action(action, target, save_distance(actor, target, action.range_ft)):
            return [target]
    return []


def resolve_save_action_turn(
    sequence: int, round_number: int, actor: EncounterCombatant, setup: EncounterSetup, dice,
    *, resource_backed_only: bool,
) -> tuple[list[BattleEvent], int, bool]:
    if not is_available(actor.state, "action"):
        return [], sequence, False
    affected = [member.state for member in [*setup.heroes, *setup.monsters]]
    for action in actor.state.template.saving_throw_actions:
        if resource_backed_only != (action.resource_id is not None):
            continue
        if not save_action_resource_available(actor.state, action):
            continue
        targets = _targets_for_action(actor, setup, action)
        if not targets:
            continue
        events: list[BattleEvent] = []
        shared_damage_rolls: list[int] | None = None
        for index, target in enumerate(targets):
            event = resolve_save_action(
                sequence, round_number, actor, target, action,
                save_distance(actor, target, action.range_ft), dice,
                spend_action=index == 0, spend_resource_cost=index == 0,
                shared_damage_rolls=shared_damage_rolls, affected_states=affected,
            )
            events.append(event); sequence += 1
            if shared_damage_rolls is None and event.damage_components:
                shared_damage_rolls = list(event.damage_components[0].rolls)
        return events, sequence, True
    return [], sequence, False
