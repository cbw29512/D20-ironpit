from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import can_see
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.encounter_targeting import combatant_distance
from app.combat.pit_policy import target_order
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def choose_multi_target_save_action(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[SavingThrowAction, tuple[EncounterCombatant, ...]] | None:
    """Choose one capped hostile saving-throw action from universal action data."""
    try:
        if not is_available(actor.state, "action"):
            return None
        for action in actor.state.template.saving_throw_actions:
            if action.action_cost != "action" or action.max_targets <= 1:
                continue
            if not action_resource_available(actor.state, action):
                continue
            legal_targets: list[EncounterCombatant] = []
            for target in target_order(actor, setup):
                distance = combatant_distance(actor, target)
                if not legal_save_action(action, target, distance):
                    continue
                if action.requires_target_sight and not can_see(actor.state, target.state, distance):
                    continue
                legal_targets.append(target)
                if len(legal_targets) >= action.max_targets:
                    break
            if legal_targets:
                return action, tuple(legal_targets)
        return None
    except Exception as exc:
        logger.exception("Failed to choose multi-target save action for %s.", actor.combatant_id)
        raise RuntimeError("Multi-target save action selection could not be resolved.") from exc


def resolve_multi_target_save_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    selection: tuple[SavingThrowAction, tuple[EncounterCombatant, ...]],
) -> tuple[list[BattleEvent], int]:
    """Spend one Action/resource, then resolve one independent save per selected target."""
    try:
        action, targets = selection
        if not targets or len(targets) > action.max_targets:
            raise ValueError("Multi-target save selection violates the declared target cap.")
        if not is_available(actor.state, action.action_cost):
            raise ValueError(f"{action.name} Action is unavailable.")
        if not action_resource_available(actor.state, action):
            raise ValueError(f"{action.name} resource is unavailable.")

        # Validate every target before mutating action economy or resources.
        for target in targets:
            distance = combatant_distance(actor, target)
            if not legal_save_action(action, target, distance):
                raise ValueError(f"{action.name} has an illegal selected target.")
            if action.requires_target_sight and not can_see(actor.state, target.state, distance):
                raise ValueError(f"{action.name} requires every selected target to be visible.")

        remaining = spend_action_resource(actor.state, action)
        spend(actor.state, action.action_cost)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        events: list[BattleEvent] = []
        for target in targets:
            resolved, sequence = resolve_save_event_chain(
                sequence,
                round_number,
                actor,
                target,
                action,
                combatant_distance(actor, target),
                dice,
                setup,
                spend_action=False,
                check_resource=False,
                spend_resource=False,
                resource_remaining_override=remaining,
                affected_states=affected_states,
            )
            events.extend(resolved)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed multi-target save action for %s.", actor.combatant_id)
        raise RuntimeError("Multi-target save action could not be resolved.") from exc
