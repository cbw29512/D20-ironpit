from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.area_save_actions import resolve_area_save
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.pit_policy import save_distance, target_order
from app.combat.encounter_targeting import combatant_distance
from app.combat.resource_conversion import restoration_conversion, resolve_resource_conversion
from app.combat.resources import action_resource_available
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def _resource_ready_or_restorable(
    actor: EncounterCombatant,
    action: SavingThrowAction,
    turn_key: str | None = None,
) -> bool:
    try:
        if action_resource_available(actor.state, action):
            return True
        return (
            action.resource_id is not None
            and restoration_conversion(actor.state, action.resource_id, turn_key) is not None
        )
    except Exception:
        logger.exception("Failed bonus-save resource check for %s.", actor.combatant_id)
        raise


def choose_bonus_save_action(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str | None = None,
):
    """Choose one legal Bonus Action saving-throw ability without consuming the normal Action."""
    try:
        if not is_available(actor.state, "bonus_action"):
            return None
        for action in actor.state.template.saving_throw_actions:
            if action.action_cost != "bonus_action" or not _resource_ready_or_restorable(actor, action, turn_key):
                continue
            if action.area is not None:
                placements = legal_area_save_placements(actor, setup, action)
                if placements:
                    return action, placements[0], None, 0
                continue
            # A living combatant at 0 HP is not in ordinary active-target order.
            # Target these creatures only when source data declares a finisher.
            if action.requires_target_zero_hp_alive:
                others = [m for m in [*setup.heroes, *setup.monsters]
                          if m.combatant_id != actor.combatant_id
                          and (action.target_scope == "all-other-creatures" or m.side != actor.side)
                          and m.state.is_alive and not m.state.is_dead
                          and m.state.current_hp == 0]
                targets = sorted(others, key=lambda m: (m.side == actor.side,
                                  combatant_distance(actor, m), m.combatant_id))
            else:
                targets = target_order(actor, setup)
            for target in targets:
                distance = save_distance(actor, target, action.range_ft)
                if legal_save_action(action, target, distance, source_id=actor.combatant_id, actor=actor):
                    return action, None, target, distance
        return None
    except Exception:
        logger.exception("Failed to choose Bonus Action save for %s.", actor.combatant_id)
        raise


def resolve_bonus_save_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve a selected Bonus Action save, restoring its resource on demand when declared."""
    try:
        turn_key = f"{round_number}:{actor.combatant_id}"
        choice = choose_bonus_save_action(actor, setup, turn_key)
        if choice is None:
            return [], sequence
        action, placement, target, distance = choice
        events: list[BattleEvent] = []
        if not action_resource_available(actor.state, action):
            if action.resource_id is None:
                raise ValueError(f"{action.name} has no restorable resource.")
            conversion = restoration_conversion(actor.state, action.resource_id, turn_key)
            if conversion is None:
                raise ValueError(f"{action.name} resource cannot be restored.")
            events.append(resolve_resource_conversion(
                actor.state,
                conversion,
                sequence=sequence,
                round_number=round_number,
                actor_id=actor.combatant_id,
                turn_key=turn_key,
            ))
            sequence += 1
        if placement is not None:
            resolved, sequence = resolve_area_save(
                sequence, round_number, actor, setup, action, placement, dice,
            )
            events.extend(resolved)
            return events, sequence
        if target is None:
            raise ValueError(f"{action.name} has no resolved target.")
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        resolved, sequence = resolve_save_event_chain(
            sequence,
            round_number,
            actor,
            target,
            action,
            distance,
            dice,
            setup,
            affected_states=affected,
        )
        events.extend(resolved)
        return events, sequence
    except Exception:
        logger.exception("Failed to resolve Bonus Action save for %s.", actor.combatant_id)
        raise
