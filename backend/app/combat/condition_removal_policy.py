from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import ConditionRemovalAction

logger = logging.getLogger(__name__)

# Lower is more urgent. This is deterministic Iron Pit AI policy, not a RAW rule.
CONDITION_PRIORITY = {
    "paralyzed": 0, "stunned": 0, "incapacitated": 0, "petrified": 0,
    "blinded": 1, "restrained": 1,
    "poisoned": 2, "frightened": 2, "charmed": 2,
    "deafened": 3, "grappled": 3,
    "prone": 4, "exhaustion": 4,
}


def distance(a: EncounterCombatant, b: EncounterCombatant) -> int:
    return abs(a.position_ft - b.position_ft)


def target_allowed(remover: EncounterCombatant, target: EncounterCombatant, action: ConditionRemovalAction) -> bool:
    if target.state.is_dead or not target.state.is_alive or target.side != remover.side:
        return False
    if distance(remover, target) > action.range_ft:
        return False
    if action.target_mode == "self":
        return target.combatant_id == remover.combatant_id
    if action.target_mode == "ally":
        return target.combatant_id != remover.combatant_id
    return True


def resource(member: EncounterCombatant, resource_id: str):
    return next((item for item in member.state.resources if item.id == resource_id), None)


def costs(action: ConditionRemovalAction, condition_count: int) -> dict[str, int]:
    result = dict(action.resource_costs)
    for resource_id, per_condition in action.resource_costs_per_condition.items():
        result[resource_id] = result.get(resource_id, 0) + per_condition * condition_count
    return result


def resources_available(member: EncounterCombatant, action: ConditionRemovalAction, condition_count: int) -> bool:
    return all(
        (item := resource(member, resource_id)) is not None and item.current_uses >= cost
        for resource_id, cost in costs(action, condition_count).items()
    )


def _effect_allows_removal(target: EncounterCombatant, condition_id: str, action_id: str) -> bool:
    effects = [effect for effect in target.state.timed_effects if effect.effect_id == condition_id]
    return all(
        not effect.allowed_removal_action_ids or action_id in effect.allowed_removal_action_ids
        for effect in effects
    )


def removable(target: EncounterCombatant, action: ConditionRemovalAction) -> list[str]:
    allowed = set(action.removable_conditions)
    return sorted(
        (
            effect for effect in target.state.active_effect_ids
            if effect in allowed and _effect_allows_removal(target, effect, action.id)
        ),
        key=lambda effect: (CONDITION_PRIORITY.get(effect, 9), effect),
    )


def affordable_conditions(remover: EncounterCombatant, target: EncounterCombatant, action: ConditionRemovalAction) -> list[str]:
    result = removable(target, action)[: action.max_conditions_per_use]
    while result and not resources_available(remover, action, len(result)):
        result.pop()
    return result


def choose_condition_removal_action(
    remover: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[ConditionRemovalAction, EncounterCombatant, list[str]] | None:
    """Choose a legal on-turn removal. Reaction removals require their trigger hook."""
    try:
        allies = setup.heroes if remover.side == "heroes" else setup.monsters
        choices: list[tuple[ConditionRemovalAction, EncounterCombatant, list[str]]] = []
        for action in remover.state.template.condition_removal_actions:
            if action.action_cost == "reaction" or not is_available(remover.state, action.action_cost):
                continue
            if action.expends_spell_slot and not slot_spell_available(remover.state, turn_key):
                continue
            for target in allies:
                if not target_allowed(remover, target, action):
                    continue
                conditions = affordable_conditions(remover, target, action)
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
                distance(remover, choice[1]),
            ),
        )
    except Exception as exc:
        logger.exception("Condition-removal choice failed for %s.", remover.combatant_id)
        raise RuntimeError("Condition-removal policy could not be evaluated.") from exc
