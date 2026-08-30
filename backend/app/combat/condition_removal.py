from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, ConditionRemovalAction

logger = logging.getLogger(__name__)

# Lower is more urgent. This is AI policy, not a rules claim: legality is determined
# entirely by the printed action and current combat state.
CONDITION_PRIORITY = {
    "paralyzed": 0,
    "stunned": 0,
    "incapacitated": 0,
    "petrified": 0,
    "blinded": 1,
    "restrained": 1,
    "poisoned": 2,
    "frightened": 2,
    "charmed": 2,
    "deafened": 3,
    "grappled": 3,
    "prone": 4,
    "exhaustion": 4,
}


def _distance(a: EncounterCombatant, b: EncounterCombatant) -> int:
    return abs(a.position_ft - b.position_ft)


def _target_allowed(remover: EncounterCombatant, target: EncounterCombatant, action: ConditionRemovalAction) -> bool:
    if target.state.is_dead or not target.state.is_alive or target.side != remover.side:
        return False
    if _distance(remover, target) > action.range_ft:
        return False
    if action.target_mode == "self":
        return target.combatant_id == remover.combatant_id
    if action.target_mode == "ally":
        return target.combatant_id != remover.combatant_id
    return True


def _resource(member: EncounterCombatant, resource_id: str):
    return next((item for item in member.state.resources if item.id == resource_id), None)


def _costs(action: ConditionRemovalAction, condition_count: int) -> dict[str, int]:
    costs = dict(action.resource_costs)
    for resource_id, per_condition in action.resource_costs_per_condition.items():
        costs[resource_id] = costs.get(resource_id, 0) + per_condition * condition_count
    return costs


def _resources_available(member: EncounterCombatant, action: ConditionRemovalAction, condition_count: int) -> bool:
    return all(
        (resource := _resource(member, resource_id)) is not None and resource.current_uses >= cost
        for resource_id, cost in _costs(action, condition_count).items()
    )


def _removable(target: EncounterCombatant, action: ConditionRemovalAction) -> list[str]:
    allowed = set(action.removable_conditions)
    return sorted(
        (effect for effect in target.state.active_effect_ids if effect in allowed),
        key=lambda effect: (CONDITION_PRIORITY.get(effect, 9), effect),
    )


def _affordable_conditions(
    remover: EncounterCombatant,
    target: EncounterCombatant,
    action: ConditionRemovalAction,
) -> list[str]:
    candidates = _removable(target, action)[: action.max_conditions_per_use]
    while candidates and not _resources_available(remover, action, len(candidates)):
        candidates.pop()
    return candidates


def choose_condition_removal_action(
    remover: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[ConditionRemovalAction, EncounterCombatant, list[str]] | None:
    """Choose a legal on-turn 2024 condition removal; Reactions are handled by trigger hooks."""
    try:
        allies = setup.heroes if remover.side == "heroes" else setup.monsters
        choices: list[tuple[ConditionRemovalAction, EncounterCombatant, list[str]]] = []
        for action in remover.state.template.condition_removal_actions:
            if action.action_cost == "reaction" or not is_available(remover.state, action.action_cost):
                continue
            for target in allies:
                if not _target_allowed(remover, target, action):
                    continue
                conditions = _affordable_conditions(remover, target, action)
                if conditions:
                    choices.append((action, target, conditions))
        if not choices:
            return None
        return min(
            choices,
            key=lambda choice: (
                CONDITION_PRIORITY.get(choice[2][0], 9),
                0 if choice[0].action_cost == "bonus_action" else 1,
                -len(choice[2]),
                _distance(remover, choice[1]),
            ),
        )
    except Exception as exc:
        logger.exception("Condition-removal choice failed for %s.", remover.combatant_id)
        raise RuntimeError("Condition-removal policy could not be evaluated.") from exc


def _remove_condition(target: EncounterCombatant, condition_id: str) -> None:
    target.state.active_effect_ids = [item for item in target.state.active_effect_ids if item != condition_id]
    target.state.timed_effects = [item for item in target.state.timed_effects if item.effect_id != condition_id]
    if condition_id == "grappled":
        target.state.grapple_sources = []


def resolve_condition_removal(
    sequence: int,
    round_number: int,
    remover: EncounterCombatant,
    target: EncounterCombatant,
    action: ConditionRemovalAction,
    condition_ids: list[str],
) -> BattleEvent:
    """Spend the printed economy/resources and end only conditions this action is allowed to remove."""
    try:
        if action.action_cost == "reaction":
            raise ValueError("Reaction condition removal requires a matching trigger, not an on-turn resolution.")
        if not _target_allowed(remover, target, action) or not condition_ids:
            raise ValueError("Condition-removal action is not legal for this target.")
        legal = set(_affordable_conditions(remover, target, action))
        if any(condition_id not in legal for condition_id in condition_ids):
            raise ValueError("Attempted to remove a condition this action cannot legally remove.")
        spend(remover.state, action.action_cost)
        for resource_id, cost in _costs(action, len(condition_ids)).items():
            resource = _resource(remover, resource_id)
            if resource is None or resource.current_uses < cost:
                raise ValueError(f"Required resource {resource_id} is unavailable.")
            resource.current_uses -= cost
        for condition_id in condition_ids:
            _remove_condition(target, condition_id)
        names = ", ".join(condition_id.replace("_", " ").title() for condition_id in condition_ids)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=remover.combatant_id,
            actor_name=remover.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            removed_condition_ids=condition_ids,
            feature_id=action.id,
            animation=action.animation,
            description=f"{remover.state.template.name} uses {action.name} on {target.state.template.name}; {names} ends.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Condition removal failed: %s -> %s.", remover.combatant_id, target.combatant_id)
        raise RuntimeError("Condition removal could not be resolved.") from exc
