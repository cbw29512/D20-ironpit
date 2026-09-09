from __future__ import annotations

from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.combat_ir import AutomaticResolutionIR, CombatActionIR
from app.domain.combat_ir_effects import ConditionRemovalEffectIR, HealingEffectIR
from app.domain.combat_ir_triggers import ConditionAppliedTriggerIR


def _single_effect(action: CombatActionIR, effect_type: type):
    if not isinstance(action.resolution, AutomaticResolutionIR):
        raise ValueError(f"Support action {action.id} must use automatic resolution.")
    if action.primary_damage is not None or len(action.effects) != 1:
        raise ValueError(f"Support action {action.id} must contain exactly one support effect and no damage.")
    effect = action.effects[0]
    if not isinstance(effect, effect_type):
        raise ValueError(f"Support action {action.id} has incompatible effect {effect.kind}.")
    return effect


def healing_ir_to_action(action: CombatActionIR) -> HealingAction:
    effect = _single_effect(action, HealingEffectIR)
    if action.action_cost == "reaction":
        raise ValueError(f"Legacy healing action {action.id} cannot represent reaction trigger semantics.")
    if action.targeting.target_mode not in {"self", "ally", "self_or_ally", "other"}:
        raise ValueError(f"Legacy healing action {action.id} has invalid target mode.")
    if len(action.resource_costs) > 1 or any(cost.mode != "per_use" for cost in action.resource_costs):
        raise ValueError(f"Legacy healing action {action.id} cannot represent these resource costs.")
    resource = action.resource_costs[0] if action.resource_costs else None
    return HealingAction(
        id=action.id,
        name=action.name,
        action_cost=action.action_cost,
        range_ft=action.targeting.range_ft,
        target_mode=action.targeting.target_mode,
        dice_count=effect.dice_count,
        dice_size=effect.dice_size,
        healing_bonus=effect.bonus,
        resource_id=None if resource is None else resource.resource_id,
        resource_cost=1 if resource is None else resource.amount,
        animation=action.animation,
    )


def _legacy_condition_trigger(action: CombatActionIR) -> str | None:
    trigger = action.reaction_trigger
    if trigger is None:
        return None
    if not isinstance(trigger, ConditionAppliedTriggerIR):
        raise ValueError(f"Condition-removal action {action.id} has incompatible reaction trigger {trigger.kind}.")
    return "condition_applied_to_self" if trigger.subject == "self" else "condition_applied_to_ally"


def condition_removal_ir_to_action(action: CombatActionIR) -> ConditionRemovalAction:
    effect = _single_effect(action, ConditionRemovalEffectIR)
    if action.targeting.target_mode not in {"self", "ally", "self_or_ally"}:
        raise ValueError(f"Legacy condition-removal action {action.id} has invalid target mode.")
    per_use: dict[str, int] = {}
    per_condition: dict[str, int] = {}
    for cost in action.resource_costs:
        target = per_use if cost.mode == "per_use" else per_condition
        target[cost.resource_id] = cost.amount
    return ConditionRemovalAction(
        id=action.id,
        name=action.name,
        action_cost=action.action_cost,
        range_ft=action.targeting.range_ft,
        target_mode=action.targeting.target_mode,
        removable_conditions=list(effect.removable_conditions),
        max_conditions_per_use=effect.max_conditions_per_use,
        resource_costs=per_use,
        resource_costs_per_condition=per_condition,
        reaction_trigger=_legacy_condition_trigger(action),
        expends_spell_slot=effect.expends_spell_slot,
        animation=action.animation,
    )
