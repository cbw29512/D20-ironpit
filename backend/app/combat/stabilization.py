from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.zero_hp import stabilize_zero_hp
from app.domain.actions import StabilizationAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _distance(a: EncounterCombatant, b: EncounterCombatant) -> int:
    return abs(a.position_ft - b.position_ft)


def _resource_available(actor: EncounterCombatant, action: StabilizationAction) -> bool:
    if action.resource_id is None:
        return True
    resource = next((item for item in actor.state.resources if item.id == action.resource_id), None)
    return resource is not None and resource.current_uses >= action.resource_cost


def _target_allowed(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: StabilizationAction,
) -> bool:
    state = target.state
    if (
        state.template.kind != "character"
        or state.is_dead
        or not state.is_alive
        or state.current_hp != 0
        or state.is_stable
        or _distance(actor, target) > action.range_ft
    ):
        return False
    if action.target_mode == "self":
        return actor.combatant_id == target.combatant_id
    if action.target_mode == "ally":
        return actor.combatant_id != target.combatant_id and actor.side == target.side
    if action.target_mode == "other":
        return actor.combatant_id != target.combatant_id
    return actor.side == target.side


def choose_stabilization_action(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[StabilizationAction, EncounterCombatant] | None:
    if not actor.state.template.stabilization_actions:
        return None
    allies = setup.heroes if actor.side == "heroes" else setup.monsters
    choices: list[tuple[StabilizationAction, EncounterCombatant]] = []
    for action in actor.state.template.stabilization_actions:
        if not is_available(actor.state, action.action_cost) or not _resource_available(actor, action):
            continue
        targets = [target for target in allies if _target_allowed(actor, target, action)]
        if not targets:
            continue
        target = max(
            targets,
            key=lambda item: (
                item.state.death_save_failures,
                -item.state.death_save_successes,
                item.combatant_id,
            ),
        )
        choices.append((action, target))
    return choices[0] if choices else None


def resolve_stabilization(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: StabilizationAction,
) -> BattleEvent:
    try:
        if not is_available(actor.state, action.action_cost):
            raise ValueError("Stabilization action cost is unavailable.")
        if not _resource_available(actor, action) or not _target_allowed(actor, target, action):
            raise ValueError("Stabilization action is not legal for this target.")
        successes_before = target.state.death_save_successes
        failures_before = target.state.death_save_failures
        spend(actor.state, action.action_cost)
        remaining = None
        if action.resource_id is not None:
            resource = next(item for item in actor.state.resources if item.id == action.resource_id)
            resource.current_uses -= action.resource_cost
            remaining = resource.current_uses
        if not stabilize_zero_hp(target.state):
            raise ValueError("Target could not be stabilized.")
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            hp_before=0,
            hp_after=0,
            death_save_successes_before=successes_before,
            death_save_failures_before=failures_before,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=True,
            is_dead=False,
            feature_id=action.id,
            resource_remaining=remaining,
            animation=action.animation,
            description=(
                f"{actor.state.template.name} uses {action.name} on "
                f"{target.state.template.name}; the target is stable at 0 HP."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Stabilization resolution failed for %s.", actor.combatant_id)
        raise RuntimeError("Stabilization action could not be resolved.") from exc
