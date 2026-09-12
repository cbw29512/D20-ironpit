from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def validate_save_targets(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    target_ids: tuple[str, ...],
    skip_range_check: bool = False,
) -> list[EncounterCombatant]:
    if not target_ids or len(set(target_ids)) != len(target_ids):
        raise ValueError("Multi-target save actions require unique target IDs.")
    by_id = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    expected_side = "monsters" if actor.side == "heroes" else "heroes"
    result: list[EncounterCombatant] = []
    for target_id in target_ids:
        target = by_id.get(target_id)
        if target is None: raise ValueError(f"Unknown save-action target {target_id!r}.")
        if target.side != expected_side: raise ValueError("Offensive Iron Pit save actions cannot target allies.")
        if not target.state.is_alive or target.state.is_dead or target.state.current_hp <= 0:
            raise ValueError(f"Save-action target {target_id!r} is not active.")
        distance_ft = 0 if skip_range_check else combatant_distance(actor, target)
        if not legal_save_action(action, target, distance_ft):
            raise ValueError(f"{action.name} cannot legally affect {target.state.template.name}.")
        result.append(target)
    return result


def resolve_save_targets(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action: SavingThrowAction,
    target_ids: tuple[str, ...],
    dice,
    *,
    skip_range_check: bool = False,
) -> tuple[list[BattleEvent], int]:
    """Resolve independent saves using one shared damage roll and one resource spend."""
    try:
        targets = validate_save_targets(actor, setup, action, target_ids, skip_range_check)
        if not action_resource_available(actor.state, action):
            raise ValueError(f"{action.name} resource is unavailable.")
        resource_remaining = spend_action_resource(actor.state, action)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        shared = [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)] if action.damage_dice_count else None
        events: list[BattleEvent] = []
        for target in targets:
            event = resolve_save_action(
                sequence, round_number, actor, target, action,
                0 if skip_range_check else combatant_distance(actor, target), dice,
                spend_action=False, check_resource=False, spend_resource=False,
                shared_damage_rolls=shared, affected_states=affected_states,
            )
            if action.resource_id is not None:
                event.resource_remaining = resource_remaining
            events.append(event); sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed multi-target save resolution for %s.", action.id)
        raise
