from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_removal_policy import (
    choose_condition_removal_action,
    costs,
    resource,
    removable,
    resources_available,
    target_allowed,
)
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.restoration_riders import apply_restoration_riders
from app.combat.timed_condition_lifecycle import remove_effect_group, remove_effect_instance
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, ConditionRemovalAction

logger = logging.getLogger(__name__)


def remove_condition(target: EncounterCombatant, condition_id: str) -> None:
    try:
        for effect in list(target.state.timed_effects):
            if effect.effect_id != condition_id:
                continue
            siblings = any(
                item.source_id == effect.source_id and item.source_effect_id == effect.source_effect_id
                and item.effect_id != condition_id for item in target.state.timed_effects
            )
            if effect.source_effect_id is not None and not siblings:
                remove_effect_group(target.state, effect)
            else:
                remove_effect_instance(target.state, effect)
        target.state.active_effect_ids = [item for item in target.state.active_effect_ids if item != condition_id]
        if condition_id == "grappled":
            target.state.grapple_sources = []
    except Exception:
        logger.exception("Failed to end condition %s on %s.", condition_id, target.combatant_id)
        raise


def resolve_condition_removal(
    sequence: int,
    round_number: int,
    remover: EncounterCombatant,
    target: EncounterCombatant,
    action: ConditionRemovalAction,
    condition_ids: list[str],
    turn_key: str,
) -> BattleEvent:
    """Spend printed economy/resources and end only conditions this action can remove."""
    try:
        if action.action_cost == "reaction":
            raise ValueError("Reaction condition removal requires a matching trigger, not an on-turn resolution.")
        if not target_allowed(remover, target, action) or not condition_ids:
            raise ValueError("Condition-removal action is not legal for this target.")
        if action.expends_spell_slot and not slot_spell_available(remover.state, turn_key):
            raise ValueError("A spell slot has already been expended to cast a spell on this turn.")
        if len(condition_ids) != len(set(condition_ids)) or len(condition_ids) > action.max_conditions_per_use:
            raise ValueError("Condition-removal request exceeds its distinct-condition limit.")
        legal = set(removable(target, action))
        if any(condition_id not in legal for condition_id in condition_ids):
            raise ValueError("Attempted to remove a condition this action cannot legally remove.")
        if not is_available(remover.state, action.action_cost) or not resources_available(remover, action, len(condition_ids)):
            raise ValueError("Condition-removal economy or resources are unavailable.")
        spend(remover.state, action.action_cost)
        if action.expends_spell_slot:
            mark_slot_spell_cast(remover.state, turn_key)
        payments = costs(action, len(condition_ids))
        for resource_id, cost in payments.items():
            item = resource(remover, resource_id)
            if item is None or item.current_uses < cost:
                raise ValueError(f"Required resource {resource_id} is unavailable.")
            item.current_uses -= cost
        rider_ids = {
            "exhaustion",
            "curse",
            "ability-score-reduction",
            "hit-point-maximum-reduction",
        }
        ordinary = [item for item in condition_ids if item not in rider_ids]
        for condition_id in ordinary:
            remove_condition(target, condition_id)
        if any(item in rider_ids for item in condition_ids):
            apply_restoration_riders(target, action, condition_ids)
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
            resource_remaining=resource(remover, next(iter(payments))).current_uses if len(payments) == 1 else None,
            feature_id=action.id,
            animation=action.animation,
            description=f"{remover.state.template.name} uses {action.name} on {target.state.template.name}; {names} ends.",
        )
    except ValueError:
        logger.exception("Rejected condition removal: %s -> %s (%s).", remover.combatant_id, target.combatant_id, action.id)
        raise
    except Exception as exc:
        logger.exception("Condition removal failed: %s -> %s.", remover.combatant_id, target.combatant_id)
        raise RuntimeError("Condition removal could not be resolved.") from exc


__all__ = ["choose_condition_removal_action", "remove_condition", "resolve_condition_removal"]
