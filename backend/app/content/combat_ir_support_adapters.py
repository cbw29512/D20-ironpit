from __future__ import annotations

from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.combat_ir import AutomaticResolutionIR, CombatActionIR, ResourceCostIR, TargetingIR
from app.domain.combat_ir_effects import ConditionRemovalEffectIR, HealingEffectIR
from app.domain.combat_ir_triggers import ConditionAppliedTriggerIR


def healing_action_to_ir(action: HealingAction) -> CombatActionIR:
    if action.action_cost == "reaction":
        raise ValueError(f"Reaction healing action {action.id} lacks explicit trigger semantics.")
    resource_costs = []
    if action.resource_id is not None:
        resource_costs.append(ResourceCostIR(resource_id=action.resource_id, amount=action.resource_cost))
    return CombatActionIR(
        id=action.id,
        name=action.name,
        action_cost=action.action_cost,
        targeting=TargetingIR(range_ft=action.range_ft, target_mode=action.target_mode),
        resolution=AutomaticResolutionIR(),
        effects=[HealingEffectIR(
            dice_count=action.dice_count,
            dice_size=action.dice_size,
            bonus=action.healing_bonus,
        )],
        resource_costs=resource_costs,
        animation=action.animation,
    )


def _condition_trigger(action: ConditionRemovalAction) -> ConditionAppliedTriggerIR | None:
    if action.reaction_trigger is None:
        return None
    subject = "self" if action.reaction_trigger == "condition_applied_to_self" else "ally"
    return ConditionAppliedTriggerIR(subject=subject)


def condition_removal_action_to_ir(action: ConditionRemovalAction) -> CombatActionIR:
    resource_costs = [
        ResourceCostIR(resource_id=resource_id, amount=amount)
        for resource_id, amount in action.resource_costs.items()
    ]
    resource_costs.extend(
        ResourceCostIR(resource_id=resource_id, amount=amount, mode="per_selected_condition")
        for resource_id, amount in action.resource_costs_per_condition.items()
    )
    return CombatActionIR(
        id=action.id,
        name=action.name,
        action_cost=action.action_cost,
        trigger="reaction" if action.action_cost == "reaction" else "turn",
        reaction_trigger=_condition_trigger(action),
        targeting=TargetingIR(range_ft=action.range_ft, target_mode=action.target_mode),
        resolution=AutomaticResolutionIR(),
        effects=[ConditionRemovalEffectIR(
            removable_conditions=list(action.removable_conditions),
            max_conditions_per_use=action.max_conditions_per_use,
            expends_spell_slot=action.expends_spell_slot,
        )],
        resource_costs=resource_costs,
        animation=action.animation,
    )
